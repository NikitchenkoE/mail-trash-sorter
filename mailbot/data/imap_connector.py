import ssl
from mailbot.config.config import EmailConfig
from imapclient import IMAPClient

class IMapConnectorErrorError(Exception):
    """IMAP connector error."""
    pass


class IMapConnector:
    """IMAP connector."""

    def __init__(self, config: EmailConfig):
        self.config = config

    def fetch_batch_emails(self, batch_size: 0) -> []:
        # Create SSL context with appropriate verification settings
        ssl_context = None
        if self.config.imap_use_ssl:
            ssl_context = ssl.create_default_context()
            
            # Configure SSL verification level
            if not self.config.imap_verify_ssl:
                # Least secure: Skip certificate verification entirely
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            elif not self.config.imap_ssl_check_hostname:
                # Medium security: Verify certificate but not hostname
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_REQUIRED
            # else: Most secure (default): Full certificate and hostname verification
        
        with IMAPClient(
            self.config.imap_host, 
            port=self.config.imap_port,
            ssl=self.config.imap_use_ssl,
            ssl_context=ssl_context
        ) as client:
            client.login(self.config.imap_user, self.config.imap_password)
            client.select_folder(self.config.imap_folder)

            ##batch_range = f"{0+1}:{0+self.config.imap_batch_size}"
            ##resp = client.fetch(batch_range, ["RFC822.HEADER"])
            ##todo call it only when there is no persisted uid
            min_uid = min(client.search())
            max_uid = min_uid + self.config.imap_batch_size

            uids = client.search(['UID',f"{min_uid}:{max_uid}"])
            print(uids)

            meta = client.fetch(
                uids,
                [
                    b"UID",
                    b"BODYSTRUCTURE",
                    b"BODY.PEEK[HEADER.FIELDS (MESSAGE-ID FROM)]",
                ],
            )

            print(meta)
            return meta