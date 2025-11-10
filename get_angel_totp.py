import pyotp

# Your TOTP Secret
TOTP_SECRET = "LAQ5VTMK6QOU2XPPMAQIIVMCSA"

def get_current_totp():
    """Get current TOTP code for Angel One"""
    totp = pyotp.TOTP(TOTP_SECRET)
    return totp.now()

if __name__ == "__main__":
    current_totp = get_current_totp()
    print(f"Current Angel One TOTP: {current_totp}")
    print("This code is valid for 30 seconds")