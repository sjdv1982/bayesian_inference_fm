from activepapers.contents import open_documentation
from unit_tests import run_tests

with open_documentation('test_log.txt', 'w') as log:

    import reproducible_random_numbers
    run_tests(reproducible_random_numbers, log)

    import gaussian_processes
    run_tests(gaussian_processes, log)

    import fbm
    run_tests(fbm, log)

    import inference
    run_tests(inference, log)
