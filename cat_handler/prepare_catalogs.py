
from cat_handler import paths
from cat_handler.parsers import anss, gcmt


def main():
    anss.prepare_anss(paths.rawcat_anss, paths.cat_anss)
    gcmt.prepare_gcmt(paths.rawcat_gcmt_1976_2020, paths.rawcat_gcmt_2020_2025, paths.cat_gcmt)


if __name__ == '__main__':
    main()
