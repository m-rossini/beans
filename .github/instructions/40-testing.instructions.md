---
applyTo: '**'
---
# Testing Guidelines
- When I say a production class is the way I want it to be and test fails, fix the test. DSo not touch production classes
- Write tests for all new features and bug fixes
- Ensure all tests pass before submitting code
- When creating tests, always run first the ones you just created, and if they pass, then run all the tests.
- Use pytest for test, ensure it is in the requirements and in the enviroment
- Tests should ALWAYS test the behaviour and not the implementation, unless specifically asked to do so
- Implementation details do not matter, for example:
'''python
Tests should not care about ensuring service A or B is called, only that the correct result is returned
def add(a: boolean) -> int:
    if a:
        call http service A
        return 1
    else:
        call http service B
        return 0
'''
- Correct test:
'''python 
def test_add_true():
    result = add(True)
    assert result == 1 
def test_add_false():
    result = add(False)
    assert result == 0
'''
- Incorrect test:   
'''python
def test_add_true_calls_service_a(mocker):
    mock_service_a = mocker.patch("path.to.service_a")
    result = add(True)
    mock_service_a.assert_called_once()
    assert result == 1
def test_add_false_calls_service_b(mocker):
    mock_service_b = mocker.patch("path.to.service_b")
    result = add(False)
    mock_service_b.assert_called_once()
    assert result == 0
'''
- Aim for high test coverage, but do not sacrifice code quality for coverage
- Use pytest fixtures for setup and teardown of tests
- Try to use parameterized tests to reduce code duplication
- Use descriptive names for test functions to indicate what they are testing
- Run tests created for the specific feature first using MAKE specific test
- After that, when successful run all tests to ensure nothing else is broken
- Use coverage.py to measure code coverage
- Ensure make file contains entry for test
- Ensure make file containt entry for coverage and coverage report and another for logging to be seen in console