TESTING_SKILLS = {
    # ===========================
    # JavaScript / TypeScript
    # ===========================
    "jest": {
        "display": "Jest",
        "category": "testing",
        "aliases": [],
        "priority": "high",
        "related": ["javascript", "typescript", "react"],
    },
    "mocha": {
        "display": "Mocha",
        "category": "testing",
        "aliases": [],
        "priority": "medium",
        "related": ["javascript", "node.js"],
    },
    "chai": {
        "display": "Chai",
        "category": "testing",
        "aliases": [],
        "priority": "medium",
        "related": ["mocha"],
    },
    "react testing library": {
        "display": "React Testing Library",
        "category": "testing",
        "aliases": [
            "@testing-library/react",
            "testing library",
        ],
        "priority": "high",
        "related": ["react", "jest"],
    },
    "cypress": {
        "display": "Cypress",
        "category": "testing",
        "aliases": [],
        "priority": "high",
        "related": ["javascript", "frontend testing"],
    },
    "playwright": {
        "display": "Playwright",
        "category": "testing",
        "aliases": [],
        "priority": "high",
        "related": ["browser testing", "e2e testing"],
    },
    # ===========================
    # Python
    # ===========================
    "pytest": {
        "display": "PyTest",
        "category": "testing",
        "aliases": ["py.test"],
        "priority": "high",
        "related": ["python", "unit testing"],
    },
    "unittest": {
        "display": "unittest",
        "category": "testing",
        "aliases": [],
        "priority": "medium",
        "related": ["python", "unit testing"],
    },
    # ===========================
    # Java
    # ===========================
    "junit": {
        "display": "JUnit",
        "category": "testing",
        "aliases": [
            "junit 4",
            "junit 5",
        ],
        "priority": "high",
        "related": ["java", "unit testing"],
    },
    "testng": {
        "display": "TestNG",
        "category": "testing",
        "aliases": [],
        "priority": "medium",
        "related": ["java"],
    },
    # ===========================
    # .NET
    # ===========================
    "xunit": {
        "display": "xUnit",
        "category": "testing",
        "aliases": [],
        "priority": "medium",
        "related": ["dotnet", "unit testing"],
    },
    "nunit": {
        "display": "NUnit",
        "category": "testing",
        "aliases": [],
        "priority": "medium",
        "related": ["dotnet", "unit testing"],
    },
    # ===========================
    # Browser / E2E
    # ===========================
    "selenium": {
        "display": "Selenium",
        "category": "testing",
        "aliases": [
            "selenium webdriver",
        ],
        "priority": "high",
        "related": ["e2e testing", "browser testing"],
    },
    "webdriver": {
        "display": "WebDriver",
        "category": "testing",
        "aliases": [
            "web driver",
        ],
        "priority": "medium",
        "related": ["selenium"],
    },
    # ===========================
    # API Testing
    # ===========================
    "postman": {
        "display": "Postman",
        "category": "testing",
        "aliases": [],
        "priority": "high",
        "related": ["api testing", "rest api"],
    },
    "insomnia": {
        "display": "Insomnia",
        "category": "testing",
        "aliases": [],
        "priority": "medium",
        "related": ["api testing", "rest api"],
    },
    # ===========================
    # Testing Concepts
    # ===========================
    "unit testing": {
        "display": "Unit Testing",
        "category": "testing",
        "aliases": [
            "unit tests",
        ],
        "priority": "high",
        "related": ["pytest", "jest", "junit"],
    },
    "integration testing": {
        "display": "Integration Testing",
        "category": "testing",
        "aliases": [
            "integration tests",
        ],
        "priority": "high",
        "related": ["unit testing", "api testing"],
    },
    "end to end testing": {
        "display": "End-to-End Testing",
        "category": "testing",
        "aliases": [
            "e2e testing",
            "e2e tests",
            "end-to-end testing",
        ],
        "priority": "high",
        "related": ["cypress", "playwright", "selenium"],
    },
    "api testing": {
        "display": "API Testing",
        "category": "testing",
        "aliases": [
            "api tests",
        ],
        "priority": "high",
        "related": ["postman", "rest api"],
    },
    "test automation": {
        "display": "Test Automation",
        "category": "testing",
        "aliases": [
            "automated testing",
            "automated tests",
        ],
        "priority": "high",
        "related": ["unit testing", "integration testing"],
    },
    "test driven development": {
        "display": "Test-Driven Development",
        "category": "testing",
        "aliases": [
            "tdd",
        ],
        "priority": "medium",
        "related": ["unit testing"],
    },
    "behavior driven development": {
        "display": "Behavior-Driven Development",
        "category": "testing",
        "aliases": [
            "bdd",
        ],
        "priority": "medium",
        "related": ["testing"],
    },
    "mocking": {
        "display": "Mocking",
        "category": "testing",
        "aliases": [
            "mock testing",
            "mock objects",
        ],
        "priority": "medium",
        "related": ["unit testing"],
    },
    "code coverage": {
        "display": "Code Coverage",
        "category": "testing",
        "aliases": [
            "test coverage",
        ],
        "priority": "medium",
        "related": ["unit testing", "integration testing"],
    },
    "go test": {
        "display": "Go Test",
        "category": "testing",
        "aliases": [
            "gotest",
            "go testing",
        ],
        "priority": "high",
        "related": ["go", "unit testing", "integration testing"],
    },
}
