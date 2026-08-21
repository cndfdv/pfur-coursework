import re

with open("data/regular.txt") as f:
    s = f.read()
    emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", s)
    phones = re.findall(r"\+7\s?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}", s)
    capitals = re.findall(r" [A-Z][a-z]+", s)

with open("result/emails.txt", "w") as f:
    for el in emails:
        f.write(el)

with open("result/phones.txt", "w") as f:
    for el in phones:
        f.write(el)

with open("result/capital_words.txt", "w") as f:
    for el in capitals:
        f.write(el)