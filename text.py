def generate_currency_with_network(currency):
    currency_text = currency['text']
    currency_network = currency['network']

    text = ""
    text += f"{currency_text.upper()}"
    text += f" ({currency_network})" if currency_network else ""

    return text

def start_text():
    text = "Welcome to Wash Bot! \nTo anonymise, please input <em>/wash</em>"
    return text

def wait_text():
    text = "Loading..."
    return text

def from_currency_text():
    text = "Please select the currency you wish to exchange :"
    return text

def to_currency_text():
    text = "Please choose currency  that you want to change to:"
    return text

def amount_text(data, min_amount, max_amount):
    
    text = ""
    text += "You are going to exchange from "
    text += generate_currency_with_network(data['from_currency'])
    text += " to "
    text += generate_currency_with_network(data['to_currency'])
    text += "\n"
    text += f"Min amount: <code>{min_amount}</code>\n"
    text += f"Max amount: <code>{max_amount}</code>\n"
    text += f"Please input the amount of "
    text += generate_currency_with_network(data['from_currency'])
    text += f" you want to exchange:"
    return text

def invalid_amount_text():
    text = "This transaction is not available.\n Please reinput the amount:"
    return text

def recipient_address_text(data):
    text = (f"You are estimated to receive <code>{data['estimated_amount']}</code> {data['to_currency']['symbol'].upper()}\n"
            f"Please input the recipient's wallet address:"
            )
    return text

def refund_address_text(data):
    text = (f"Recipient's address: <code>{data['recipient_address']}</code>. \n")
    return text

def refund_prompt_text(data):
    text = ""
    text += f"You are estimated to receive <code>{data['estimated_amount']}</code> "
    text += generate_currency_with_network(data['to_currency'])
    text += "\n"
    text += (f"In case of failed transactions or any unforeseen errors, please send your default refund address.\n"
            f"This should be the address you're sending currency from.\n"
            f"If you wish to change the standard refund address in the future write <em>/refund</em>"
            )
    return text

def refund_address_prompt(address):
    text = ""
    text += f"Refund address is <code>{address}</code>\n"
    text += f"From now, this address will be the standard refund address.\n"
    text += f"If you wish to change the standard refund address in the future write, <em>/refund</em>\n"
    text += f"Please input recipient's address:"
    return text

def confirm_text(data):
    text = ""
    text += f"You are going to wash <code>{data['amount']}</code> "
    text += generate_currency_with_network(data['from_currency'])
    text += " to "
    text += generate_currency_with_network(data['to_currency'])
    text += "\n"
    text += f"Recipient's address: \n"
    text += f"<code>{data['recipient_address']}</code> \n"
    text += f"Refund address: \n"
    text += f"<code>{data['refund_address']}</code> \n"
    text += f"Please confirm the information above. \n"
    text += f"To edit, please select the cancel button below. \n \n"
    text += f"Please note: This can take up to 8 minutes to process depending on a variety of factors."
    return text

def address_failed():
    text = (f"Please make sure if the recipient and refund address is valid! \n"
            f"If something went wrong, you can try again by <em>/wash</em>"
            )

    return text

def deposit_text(data, deposit_address, exchange_id):
    text = f"Please deposit "
    text += data['amount']
    text += " "
    text += generate_currency_with_network(data['from_currency'])
    text += f" to <code>{deposit_address}</code> \n"
    # text += f"To confirm the result, please input <em>/result</em> and type <code>{exchange_id}</code>"
    text += f"Your swap will be completed automatically and you will get notified soon!"
    return text

def result_text(deposit_address):
    text=f"Please input exchange Id"
    return text

def cancel_text():
    text="Bye! Please type <em>/wash</em>, when you want my help."
    return text

def input_sender_address():
    text=(f"In case of failed transactions or any unforeseen errors, please write your default refund address.\n"
          f"This should be the address you're sending currency from."
          )
    return text

def set_refund_address(sender_address):
    text = (f"Refund address has changed to {sender_address}\n"
            f"Please input <em>/refund</em>, if you want to change it."
            )
    return text
