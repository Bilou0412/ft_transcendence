from django.test.runner import DiscoverRunner
from termcolor import colored

class ColorTestRunner(DiscoverRunner):
    def run_suite(self, suite, **kwargs):
        result = super().run_suite(suite, **kwargs)
        self.print_results(result)
        return result

    def print_results(self, result):
        print('\n')
        if result.failures or result.errors:
            print(colored('Tests failed', 'red', attrs=['bold']))
        else:
            print(colored('All tests passed', 'green', attrs=['bold']))
        print(colored(f'Ran {result.testsRun} tests', 'cyan'))
        print(colored(f'  {len(result.failures)} failures', 'red' if result.failures else 'green'))
        print(colored(f'  {len(result.errors)} errors', 'red' if result.errors else 'green'))
        print('\n')