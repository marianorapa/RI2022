from cgi import test
import re

regex = "((?:(?:[A-Z](?:[a-z]+|\.+))+(?:\s[A-Z][a-z]+)+))"

test_string = "https://www.researchgate.net/publication/2360239 https://www.researchgate.net/publication/2360239 mratto@mail.unlu.edu.ar https://www.researchgate.net/publication/2360239 https://www.researchgate.net/publication/2360239 https://www.researchgate.net/publication/2360239 https://www.researchgate.net/publication/2360239 https://www.researchgate.net/publication/2360239 https://www.researchgate.net/publication/2360239 https://www.researchgate.net/publication/2360239 https://www.researchgate.net/publication/2360239 https://www.researchgate.net/publication/2360239 mratto@mail.unlu.edu.ar mratto@mail.unlu.edu.ar https://www.researchgate.net/publication/2360239 https://www.researchgate.net/publication/2360239 https://www.researchgate.net/publication/2360239 https://www.researchgate.net/publication/2360239 https://www.researchgate.net/publication/2360239 Domingo Faustino Sarmiento "

result = re.findall(regex, test_string)
print(result)