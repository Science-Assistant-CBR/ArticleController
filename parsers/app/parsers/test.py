import emoji


def remove_emojis(text):
    return emoji.replace_emoji(text, replace="")


# Example
text_with_emojis = "Hello 👋, how are you? 😊"
cleaned_text = remove_emojis(text_with_emojis)
print(cleaned_text)  # Output: "Hello , how are you? "
