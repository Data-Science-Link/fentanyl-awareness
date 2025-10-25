#!/bin/bash
# 🔒 Security Audit Script for Public Repository
# Run from project root: ./data_engineering/security_audit.sh

# Change to project root directory
cd "$(dirname "$0")/.."

echo "🔒 SECURITY AUDIT FOR PUBLIC REPOSITORY"
echo "======================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo "1. Checking for sensitive files in working directory..."
SENSITIVE_FILES=$(find . -name "*.env" -o -name "*secret*" -o -name "*credential*" -o -name "*key*" -o -name "service_account.json" | grep -v ".git" | grep -v "dbt_packages")
if [ -z "$SENSITIVE_FILES" ]; then
    print_status 0 "No sensitive files found in working directory"
else
    print_warning "Sensitive files found (should be ignored by git):"
    echo "$SENSITIVE_FILES"
fi

echo
echo "2. Checking if sensitive files are tracked by git..."
TRACKED_SENSITIVE=$(git ls-files | grep -E "\.(env|key|pem|p12|json)$|secret|credential|password")
if [ -z "$TRACKED_SENSITIVE" ]; then
    print_status 0 "No sensitive files tracked by git"
else
    print_status 1 "Sensitive files are tracked by git!"
    echo "$TRACKED_SENSITIVE"
fi

echo
echo "3. Checking git status for sensitive files..."
GIT_STATUS_SENSITIVE=$(git status --porcelain | grep -E "\.env|service_account\.json|*secret*|*credential*|*key*")
if [ -z "$GIT_STATUS_SENSITIVE" ]; then
    print_status 0 "No sensitive files in git status"
else
    print_status 1 "Sensitive files in git status!"
    echo "$GIT_STATUS_SENSITIVE"
fi

echo
echo "4. Checking for sensitive data in commit messages..."
COMMIT_SENSITIVE=$(git log --all --full-history -- "*" | grep -i -E "(password|secret|key|token|api|credential|env)" | head -5)
if [ -z "$COMMIT_SENSITIVE" ]; then
    print_status 0 "No sensitive data in commit messages"
else
    print_warning "Potential sensitive data in commit messages:"
    echo "$COMMIT_SENSITIVE"
fi

echo
echo "5. Checking .gitignore for comprehensive coverage..."
GITIGNORE_COVERAGE=$(grep -E "\.env|service_account|credential|secret|key" .gitignore)
if [ ! -z "$GITIGNORE_COVERAGE" ]; then
    print_status 0 ".gitignore covers sensitive files"
else
    print_status 1 ".gitignore missing sensitive file patterns"
fi

echo
echo "6. Testing .gitignore effectiveness..."
echo "test" > .env.test
if git status --porcelain | grep -q ".env.test"; then
    print_status 1 ".gitignore not working for .env files"
else
    print_status 0 ".gitignore working for .env files"
fi
rm -f .env.test

echo
echo "7. Checking for hardcoded API keys in code..."
HARDCODED_KEYS=$(grep -r -i -E "(api[_-]?key|secret[_-]?key|password|token)" --include="*.py" --include="*.js" --include="*.ts" --include="*.json" . | grep -v ".git" | grep -v "dbt_packages" | head -5)
if [ -z "$HARDCODED_KEYS" ]; then
    print_status 0 "No hardcoded API keys found in code"
else
    print_warning "Potential hardcoded keys found:"
    echo "$HARDCODED_KEYS"
fi

echo
echo "8. Checking for personal information..."
PERSONAL_INFO=$(grep -r -i -E "(email|phone|address|ssn|social)" --include="*.py" --include="*.md" --include="*.txt" . | grep -v ".git" | grep -v "dbt_packages" | head -5)
if [ -z "$PERSONAL_INFO" ]; then
    print_status 0 "No personal information found"
else
    print_warning "Potential personal information found:"
    echo "$PERSONAL_INFO"
fi

echo
echo "======================================"
echo "🔒 SECURITY AUDIT COMPLETE"
echo "======================================"

# Final recommendation
if [ -z "$TRACKED_SENSITIVE" ] && [ -z "$GIT_STATUS_SENSITIVE" ]; then
    echo -e "${GREEN}🎉 REPOSITORY APPEARS SAFE TO MAKE PUBLIC${NC}"
    echo "✅ No sensitive files tracked by git"
    echo "✅ No sensitive files in git status"
    echo "✅ .gitignore is comprehensive"
else
    echo -e "${RED}🚨 REPOSITORY NOT SAFE FOR PUBLIC RELEASE${NC}"
    echo "❌ Sensitive files detected"
    echo "❌ Please fix issues before making public"
fi

echo
echo "Next steps:"
echo "1. Review any warnings above"
echo "2. Ensure all sensitive data is in environment variables"
echo "3. Configure GitHub Secrets for CI/CD"
echo "4. Test with a private repository first"
echo "5. Monitor after going public"
