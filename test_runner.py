import os
import sys
from django.test.runner import DiscoverRunner
from django.utils import termcolors

class ColorfulTestRunner(DiscoverRunner):
    """Кастомный test runner с цветным выводом"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Настройка цветов
        self.style = termcolors.colorize
        self.success_color = {'fg': 'green', 'opts': ('bold',)}
        self.failure_color = {'fg': 'red', 'opts': ('bold',)}
        self.error_color = {'fg': 'magenta', 'opts': ('bold',)}
        self.skip_color = {'fg': 'yellow', 'opts': ('bold',)}
        self.test_color = {'fg': 'white', 'opts': ('bold',)}
    
    def run_tests(self, test_labels, **kwargs):
        print("\n" + "="*70)
        print(self.style("🚀 ЗАПУСК ТЕСТОВ", opts=('bold',)))
        print("="*70)
        
        self.setup_test_environment()
        suite = self.build_suite(test_labels, **kwargs)
        databases = self.get_databases(suite)
        old_config = self.setup_databases(aliases=databases)
        
        result = self.run_suite(suite)
        
        self.teardown_databases(old_config)
        self.teardown_test_environment()
        
        self.print_summary(result)
        return self.suite_result(suite, result)
    
    def run_suite(self, suite, **kwargs):
        """Запускает набор тестов и возвращает результат"""
        from unittest import TextTestRunner
        return TextTestRunner(
            verbosity=self.verbosity,
            failfast=self.failfast,
            resultclass=self.get_resultclass()
        ).run(suite)
    
    def get_resultclass(self):
        """Возвращает кастомный класс результата"""
        from django.test.runner import DebugSQLTextTestResult
        return DebugSQLTextTestResult
    
    def format_test_name(self, test):
        """Форматирует имя теста для красивого вывода"""
        test_str = str(test)
        # Убираем лишнюю информацию
        if ' (' in test_str:
            test_str = test_str.split(' (')[0]
        return test_str
    
    def print_summary(self, result):
        """Печатает красивую статистику"""
        print("\n" + "="*70)
        print(self.style("📊 СТАТИСТИКА ТЕСТОВ", opts=('bold',)))
        print("="*70)
        
        total = result.testsRun
        failures = len(result.failures)
        errors = len(result.errors)
        skipped = len(getattr(result, 'skipped', []))
        passed = total - failures - errors - skipped
        
        print(f"  Всего тестов: {self.style(str(total), **self.test_color)}")
        print(f"  ✅ Успешно:   {self.style(str(passed), **self.success_color)}")
        print(f"  ❌ Провалов:  {self.style(str(failures), **self.failure_color)}")
        print(f"  💥 Ошибок:    {self.style(str(errors), **self.error_color)}")
        print(f"  ⏭️  Пропущено: {self.style(str(skipped), **self.skip_color)}")
        
        if failures == 0 and errors == 0:
            print(f"\n🎉 {self.style('ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!', **self.success_color)}")
        else:
            print(f"\n😞 {self.style('ЕСТЬ ПРОБЛЕМЫ В ТЕСТАХ', **self.failure_color)}")
        print("="*70)