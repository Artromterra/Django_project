
import os
import shutil
from logging import getLogger
from uuid import uuid4

from shop.models import Product
from shop.models.category import Category
from shop.models.seller import Seller
from shop.models.product import ProductSeller
from services.importing.importers.importer_factory import ImporterFactory
from utils.logs.loggers.separator import SeparatorLogger

from .reporters.base import BaseReporter

logger = getLogger("main.services.importing")


class ImportManager(object):
    """
    The class responsible for the entire import process from files.

    The class encapsulates the logic of the complete data import process from a single file.
    The process consists of retrieving data from a file,
    transferring the import file to the desired directory, and reporting on the import result.
    """

    def __init__(
            self,
            import_file: str,
            importer_factory: ImporterFactory,
            reporter: BaseReporter,
            success_dir: str,
            failure_dir: str,
            separator_logger: SeparatorLogger
    ):
        """
        Init class.

        :param import_file: Import file path.
        :param importer_factory: Importer factory.
        :param reporter: Reporter for reporting on the import result.
        :param success_dir: The directory to which the import files will be moved
        if there were no errors in the process.
        :param failure_dir: The directory to which the import files will be moved
        if there was at least one error in the process.
        :param separator_logger: Separator logger.
        """
        if os.path.exists(import_file) and os.path.isfile(import_file):
            self.__import_file = import_file
        else:
            raise ValueError("Import file not exists or is not file.")

        self.__unique_logging_id: str = str(uuid4())
        self.__separator_logger = separator_logger
        self.__logger = separator_logger.adapter

        self.__importer_factory = importer_factory

        self.__reporter = reporter

        if os.path.isdir(success_dir):
            self.__success_dir = success_dir
        else:
            raise ValueError("Success dir must be dir.")
        if os.path.isdir(failure_dir):
            self.__failure_dir = failure_dir
        else:
            raise ValueError("Failure dir must be dir.")

    def __import_from_file(self) -> bool:
        """Import data from file."""
        self.__logger.info("Start importing from %s", self.__import_file)
        importer = self.__importer_factory(self.__import_file, self.__separator_logger)
        success: bool = True

        # import categories
        for category_dict in importer.import_categories():
            try:
                Category.objects.update_or_create(**category_dict)
            except Exception as exc:
                self.__logger.warning(
                    "Can't import category data %s\n%s",
                    str(category_dict),
                    str(exc)
                )
                success = False

        # import products
        for product_dict in importer.import_products():
            try:
                Product.objects.update_or_create(**product_dict)
            except Exception as exc:
                self.__logger.warning(
                    "Can't import product data %s\n%s",
                    str(product_dict), str(exc)
                )
                success = False

        # import sellers
        for seller_dict in importer.import_sellers():
            try:
                Seller.objects.update_or_create(**seller_dict)
            except Exception as exc:
                self.__logger.warning(
                    "Can't import seller data %s\n%s",
                    str(seller_dict), str(exc)
                )
                success = False

        # import ProductSeller
        for product_seller_dict in importer.import_products_sellers():
            try:
                ProductSeller.objects.update_or_create(**product_seller_dict)
            except Exception as exc:
                self.__logger.warning(
                    "Can't import ProductSeller data %s\n%s",
                    str(product_seller_dict),
                    str(exc)
                )
                success = False

        # explicitly closing the import file
        importer.close()
        return success

    def __move_file(self, success: bool) -> None:
        """Move import file."""
        try:
            if success:
                self.__logger.info("Import was successful.")
                shutil.move(self.__import_file, self.__success_dir)
            else:
                self.__logger.warning("Import passed with errors.")
                shutil.move(self.__import_file, self.__failure_dir)
        except Exception as exc:
            self.__logger.warning("Can't move import file %s\n%s", self.__import_file, str(exc))
        else:
            self.__logger.info("The import file has been successfully moved.")

    def __report_about_importing_file(self, success: bool) -> None:
        """Report about importing."""
        if success:
            self.__reporter.report_about_success(self.__import_file)
        else:
            self.__reporter.report_about_failure(self.__import_file)

    def run_import(self) -> None:
        """Import data from file."""
        try:
            success = self.__import_from_file()
            self.__move_file(success)
            self.__report_about_importing_file(success)
        except Exception as exc:
            self.__logger.error("Unexpected error.\n%s", str(exc))
        finally:
            # clear separate handler
            separate_handler = self.__separator_logger.handler
            separate_handler.extract(self.__separator_logger.unique_id)
