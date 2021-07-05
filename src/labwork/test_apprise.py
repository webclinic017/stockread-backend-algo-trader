import apprise

APPRISE_CONFIG_PATH = "../config/apprise.yml"

# Create an Apprise instance
apobj = apprise.Apprise()

config = apprise.AppriseConfig()
config.add(APPRISE_CONFIG_PATH)
apobj.add(config)

# Add all of the notification services by their server url.
# A sample email notification:
# apobj.add('mailto://galford2605:thuhong1710@gmail.com')

# A sample pushbullet notification
# apobj.add('discord://859610104777539604/fSSmFTheKog173x6QN5y3A4Tsuoric_wQfy6V2W4x6L5subedaWeHuhj9_IwIIzzKr-i')
# apobj.add('tgram://1677166991:AAEkQ6-UYBrfjLprr3PG0fH3vRqOY07Bv1Q/1754262232')

# Then notify these services any time you desire. The below would
# notify all of the services loaded into our Apprise object.
apobj.notify(
    body='what a great notification service!',
    title='MY NOTIFICATION TITLE',
)