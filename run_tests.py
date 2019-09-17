for file in ["tests.async_test", "tests.basic", "tests.checks", "tests.help", "tests.math"]:
    print("---------" + file + "----------")
    __import__(file)
