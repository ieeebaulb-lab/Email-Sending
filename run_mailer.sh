#!/bin/bash
# Convenience script to run the mailer with proper environment

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "======================================================================"
echo "  Formal Email Mailer - Startup Script"
echo "======================================================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python3 -c "import googleapiclient" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Dependencies not installed. Installing...${NC}"
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
    echo ""
fi

# Check for credentials.json
if [ ! -f "credentials.json" ]; then
    echo -e "${RED}✗ ERROR: credentials.json not found!${NC}"
    echo ""
    echo "Please download OAuth credentials from Google Cloud Console:"
    echo "  1. Visit: https://console.cloud.google.com/apis/credentials"
    echo "  2. Create OAuth 2.0 Client ID (Desktop app)"
    echo "  3. Download as credentials.json"
    echo "  4. Place in this directory"
    echo ""
    exit 1
fi

# Check for existing token
if [ -f "token.json" ]; then
    echo -e "${GREEN}✓ Found token.json - You won't need to login!${NC}"
else
    echo -e "${YELLOW}⚠ No token.json found - You'll need to login once${NC}"
    echo "  (After this, your credentials will be saved)"
fi

echo ""
echo "Starting mailer..."
echo "======================================================================"
echo ""

# Run the script
python3 mailer_dual_template.py

# Capture exit code
EXIT_CODE=$?

echo ""
echo "======================================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Script completed successfully${NC}"
else
    echo -e "${YELLOW}Script exited with code: $EXIT_CODE${NC}"
fi
echo "======================================================================"

exit $EXIT_CODE

