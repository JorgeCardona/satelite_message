import os
import requests
import smtplib
from email.mime.text import MIMEText

# Retrieve location data from environment variables,  https://www.google.com/maps
LATITUDE = os.getenv('LATITUDE')
LONGITUDE = os.getenv('LONGITUDE')
# https://www.advancedconverter.com/es/herramientas-de-mapa/encontrar-altitud-desde-coordenadas
ALTITUDE = os.getenv('ALTITUDE')

# Retrieve satellite data from environment variables
SATELLITE_ID = os.getenv('SATELLITE_ID')
SATELLITE_API_KEY = os.getenv('SATELLITE_API_KEY')

# Construct the satellite API URL
def construct_url(satellite_id, latitude, longitude, altitude, api_key):
    return f"https://api.n2yo.com/rest/v1/satellite/positions/{satellite_id}/{latitude}/{longitude}/{altitude}/1/&apiKey={api_key}"

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
EMAIL_USER = os.getenv('EMAIL_USER')
# https://myaccount.google.com/apppasswords
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

def send_email(message):
    """
    Sends an email with the specified message.
    
    Args:
    - message (str): The content of the email.
    """
    msg = MIMEText(message)
    msg['Subject'] = 'Satellite is passing over your area!'
    msg['From'] = EMAIL_USER
    msg['To'] = RECIPIENT_EMAIL

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, RECIPIENT_EMAIL, msg.as_string())

def get_look_direction(azimuth):
    """
    Returns the cardinal or intercardinal direction based on the azimuth angle.

    Args:
        azimuth (float): The azimuth angle in degrees (0 to 359).

    Returns:
        str: The direction to look, such as "North", "Northeast", "East", etc.
             If the azimuth is not within 0 to 359 degrees, returns "Invalid azimuth value".
    """
    if azimuth >= 0 and azimuth < 45:
        return "North"
    elif azimuth >= 45 and azimuth < 90:
        return "Northeast"
    elif azimuth >= 90 and azimuth < 135:
        return "East"
    elif azimuth >= 135 and azimuth < 180:
        return "Southeast"
    elif azimuth >= 180 and azimuth < 225:
        return "South"
    elif azimuth >= 225 and azimuth < 270:
        return "Southwest"
    elif azimuth >= 270 and azimuth < 315:
        return "West"
    elif azimuth >= 315 and azimuth < 360:
        return "Northwest"
    else:
        return "Invalid azimuth value"

def check_satellite(url_satellite):
    """
    Checks if the satellite is visible over the specified location by making a request to the satellite API.
    If the satellite is visible, sends an email notification.

    Args:
        url_satellite (str): The URL to fetch satellite position data from the API.

    Returns:
        None
    """
    response = requests.get(url_satellite)
    data = response.json()
    print('API response:', data)
    
    positions = data.get('positions', [])
    info = data.get('info', {})

    # Retrieve satellite name from info
    satellite_name = info.get('satname', 'Unknown')

    # Check each position to see if the satellite is over the location
    for position in positions:
        print('Position:', position)
        altitude_response = position.get('sataltitude', 0)
        elevation_response = position.get('elevation', 0)
        azimuth_response = position.get('azimuth', 0)
        ra = position.get('ra', 0)
        dec = position.get('dec', 0)
        timestamp = position.get('timestamp', 0)
        eclipsed = position.get('eclipsed', False)

        direction = get_look_direction(int(azimuth_response))
        print(f"Direction to look: {direction} (Azimuth: {azimuth_response}°)")
        print(f"Right Ascension: {ra}°")
        print(f"Declination: {dec}°")
        print(f"Timestamp: {timestamp}")
        print(f"Eclipsed: {'Yes' if eclipsed else 'No'}")
        
        print('Satellite Name:', satellite_name)
        print('Altitude Response:', altitude_response)
        
        # Check if the satellite is visible
        if elevation_response > 0 and not eclipsed:
            send_email(f"Satellite {satellite_name} is over your area at {azimuth_response}° azimuth. The direction to look is: {direction}!")
            print('Email sent successfully.')
            break  # Exit loop after sending the email

        else:
            print(f"Satellite {satellite_name} is not over your area. Altitude: {altitude_response} meters, Direction: {direction}, Azimuth: {azimuth_response}°, Eclipsed: {'Yes' if eclipsed else 'No'}.")

# Construct the satellite URL and run the check
url_satellite = construct_url(SATELLITE_ID, LATITUDE, LONGITUDE, ALTITUDE, SATELLITE_API_KEY)
check_satellite(url_satellite)