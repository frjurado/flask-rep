from ..email import send_email


def confirm(user, token):
    """
    args: user, token.
    Send a token for account confirmation.
    """
    send_email ( user.email,
                 "Confirm your account",
                 "mail/confirm",
                 user = user,
                 token = token )

def reset(user, token):
    """
    args: user, token.
    Send a token for username/password reset.
    """
    send_email( user.email,
                'Reset Your Username and Password',
                'mail/reset',
                user = user,
                token = token )

def change_email(user, new_email, token):
    """
    args: user, new_email, token.
    Send a token for a new email confirmation.
    """
    send_email( new_email,
                'Confirm your new email',
                'mail/change_email',
                user = user,
                token = token )
