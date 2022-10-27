import argparse
from single_bot import SingleBot


def parse_args():
    parser = argparse.ArgumentParser(description="Start auto detect crash bugs.",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--device_serial", action="store", dest="device_serial", required=True)
    parser.add_argument("--package_name", action="store", dest="package_name", required=False)
    parser.add_argument("--apk_path", action="store", dest="apk_path", required=True)
    parser.add_argument("--timeout", action="store", dest="timeout", required=False, default=60,
                        help="test time(minutes) default is 60 minutes")
    parser.add_argument("--throttle", action="store", dest="throttle", required=False, default=500,
                        help="time gaps between two events")
    parser.add_argument("--output_path", action="store", dest="output_path", required=False, default='./output/')
    parser.add_argument("--keep_app", action="store_true", dest="keep_app", required=False)
    parser.add_argument("--model_name", action="store", dest="model_name", required=False, default='random')
    parser.add_argument("--grant_permission", action="store", dest="grant_permission", required=False, default=True)

    options = parser.parse_args()
    return options


def main():
    opts = parse_args()

    singleBot = SingleBot(
        device_serial   = opts.device_serial,
        package_name    = opts.package_name,
        apk_path        = opts.apk_path,
        timeout         = opts.timeout,
        throttle        = opts.throttle,
        output_path     = opts.output_path,
        keep_app        = opts.keep_app,
        model_name      = opts.model_name,
        grant_permission= opts.grant_permission
    )
    singleBot.start()
    return


if __name__ == '__main__':
    main()