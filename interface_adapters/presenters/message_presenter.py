# messenger_frontend/interface_adapters/presenters/message_presenter.py
class MessagePresenter:
    def __init__(self):
        pass

    def format_user_list(self, users, current_user_id):
        """
        Formate la liste des utilisateurs pour l'affichage
        """
        user_dict = {}
        for user in users:
            if user['_id'] != current_user_id:
                user_dict[user['email']] = user['_id']
        return user_dict

    def format_message_for_display(self, message, current_user_id):
        """
        Formate un message pour l'affichage
        """
        return {
            'sender_id': message['senderId'],
            'content': message.get('content', {}),
            'is_from_me': message['senderId'] == current_user_id
        }