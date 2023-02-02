import argparse
from src.modules.xml import TestXmlManager


def main(args: argparse.Namespace):
    """
    Запуск скрипта в зависимости от переданных аргументов.
    :param args: Аргументы запуска скрипта.
    """
    manager = TestXmlManager()
    if args.action == "all":
        manager.generate_files(number_of_zips=args.zip_count,
                               files_in_zip=args.xml_in_zip,
                               save_dir=args.zip_dir,
                               processes=args.processes)

        manager.upload_from_files(zip_files_dir=args.zip_dir,
                                  processes=args.processes)

        manager.save_xml_data_to_csv(save_dir=args.csv_dir)

    elif args.action == "save":
        manager.generate_files(number_of_zips=args.zip_count,
                               files_in_zip=args.xml_in_zip,
                               save_dir=args.zip_dir,
                               processes=args.processes)

    elif args.action == "upload":
        manager.upload_from_files(zip_files_dir=args.zip_dir,
                                  processes=args.processes)

        manager.save_xml_data_to_csv(save_dir=args.csv_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Аргументы программы')
    parser.add_argument("--zip_dir",
                        default=__file__.split("main.py")[0] + 'files/',
                        help="Каталог для хранения zip архивов, по умолчанию каталог /files в репозитории с main.py")
    parser.add_argument("--csv_dir",
                        default=__file__.split("main.py")[0] + 'files/',
                        help="Каталог для сохранения csv файлов, по умолчанию каталог /files в репозитории с main.py")
    parser.add_argument("--action",
                        default="all",
                        choices=["all", "save", "upload"],
                        help="Действие, которое требуется совершить. По умолчанию all")
    parser.add_argument("--zip_count",
                        default=50,
                        help="Количество zip архивов, по умолчанию 50")
    parser.add_argument("--xml_in_zip",
                        default=100,
                        help="Количество файлов в zip архиве, по умолчанию 100")
    parser.add_argument("--processes",
                        default=4,
                        help="Количество процессов для распараллеливания, по умолчанию 4")

    main(parser.parse_args())
