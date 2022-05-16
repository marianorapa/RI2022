import re
from bs4 import BeautifulSoup
from bs4.element import Comment


class Tokenizer:
    def __init__(self, min_length, max_length, proper_name_splitting = False):
        self.min_length = min_length
        self.max_length = max_length
        self.PROPER_NAME_SPLITTING_ENABLED = proper_name_splitting  

    def __get_proper_names(self, line):        
        regex = "\W((?:(?:[A-Z](?:[a-z]+|\.+))+(?:\s[A-Z][a-z]+)+))"
        result = re.findall(regex, line)           
        return list(result) 
        
    def __is_date(self, token):
        regex = "(?:\s|^)(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{1,4})(?:\s|$)|(?:\s|^)(\d{2,4}[\/\.\-]\d{1,2}[\/\.\-]\d{1,2})(?:\s|$)"
        return bool(re.match(regex, token))

    def __is_number(self, token):        
        regex = "^[0-9]+$"
        regex_decimal = "^[0-9]+[\.|\,][0-9]+$"
        phones_regex = "([0-9]{1,3}?[-]?[0-9]{8,9}?)(?:$|\s)"

        return re.findall(f"{regex}|{phones_regex}|{regex_decimal}", token)

    def __is_abbreviation(self, token, collection = {}):    
        regex_1 = "(?:\A|\W)(?:[a-zA-Z](?:\.[a-zA-Z])+)(?:\Z|\W)"             # matches "i.e", "i.e.", "u.s.a", etc
        regex_2 = "(?:[A-Z][bcdfghj-np-tvxz]+\.)"                             # extracted from article, matches capital letter followed by consonants
        regex_3 = "(?:^|\W)(?:[A-Z]{2,5})(?:$|\W)"                            # matches abbreviations as capital letters with initials like NASA or JFK
        regex_4 = "(?:(?:^|\W)[bcdfghj-np-tvxz]{2,4}\.)"                      # matches all consonants ending in period
        regex_5 = "(?:[A-Z][aeiou][bcdfghj-np-tvxz]\.)"                       # matches "Lic.", "Mag."
        regex_6 = "(?:^|\W)(?:[a-zA-Z]{1,2}(?:\.[a-zA-Z]{1,2})+)(?:$|\W)"
        exists_without_last_period = False
        exists_lower = False
        if (re.match("[A-Za-z]+\.", token)):
            exists_without_last_period = token[:-1] in collection       # if it ends with period, checks if it's in the collection without it
        if (re.match("[A-Z]+", token)):
            exists_lower = token.lower() in collection
        if not exists_without_last_period and not exists_lower:
            return re.findall(f"{regex_1}|{regex_2}|{regex_3}|{regex_4}|{regex_5}|{regex_6}", token)

    def __is_mail_or_url(self, token):
        url_regex = "([A-Za-z]+:/+[A-Za-z0-9_\-\.]+\.[A-Za-z0-9_\-\./]+[^https:])"        # takes into account when there are 2 urls sticked together
        url_regex_2 = "(www\.[a-z0-9]+(?:\.[a-z]{2,4}){1,4})"
        mail_regex = "([A-Za-z0-9_\-\.]+@[A-Za-z]+(?:\.[A-Za-z]+)+)"
        return bool(re.match(f"{url_regex}|{mail_regex}|{url_regex_2}", token))

    def __remove_punctuation(self, token):
        return re.sub("[^\w\s]|_", "", token)

    def __remove_punctuation_special_token__(self, token):
        return re.sub("[^\w\s/@\.:-\?&\|]", "", token)

    def __translate(self, to_translate):
        tabin = u'áäâàãéëèêẽíïĩìîóõöòôúüùûũñ'
        tabout = u'aaaaaeeeeeiiiiiooooouuuuun'
        tabin = [ord(char) for char in tabin]
        translate_table = dict(zip(tabin, tabout))
        return to_translate.translate(translate_table)

    def __has_numbers__(self, token):
        return bool(re.match(".*[0-9]+.*", token))

    def __only_letters__(self, token):        
        return bool(re.match("\A[a-z]+\Z", token))

    def get_tokens_with_frequency(self, original_line): 
        try:
            line = self.__text_from_html__(original_line)
            if len(line) == 0:
                line = original_line # html parsing failed
        except:
            pass             
        abbreviations_list      = []
        numbers_list            = []    
        mails_urls_list         = []
        dates_list              = []

        result = {}

        line = self.__translate(line).strip()              
        # Intentar identificar nombres propios 
        proper_names_list = self.__get_proper_names(line)                
        if not self.PROPER_NAME_SPLITTING_ENABLED:
            for name in proper_names_list: 
                # Elimina los nombres identificados para que no sean tomados como tokens al separar por espacios
                line.replace(name, "")

        # Separación de la línea por espacios                    
        tokens_list = line.strip().split()                
        
        for raw_token in tokens_list:                         
            token = raw_token.strip()                                   
            special_token = False                       
            if self.__is_number(token):                
                numbers_list.append(token)   
                special_token = True     
            elif (self.__is_mail_or_url(token)):
                mails_urls_list.append(token)                                                    
                special_token = True        
                
            elif (self.__is_abbreviation(token)):
                abbreviations_list.append(token)  
                
            elif (self.__is_date(token)):                
                dates_list.append(token)
                special_token = True    
                
            if not special_token:                        
                token = self.__remove_punctuation(token).lower()                    
                if not self.__only_letters__(token):
                    continue
            else:
                token = self.__remove_punctuation_special_token__(token).lower()

            if special_token or (len(token) >= self.min_length and len(token) <= self.max_length):
                result[token] = 1 if token not in result else result[token] + 1
        
        for name in proper_names_list:
            name = self.__remove_punctuation(name).lower()
            result[name] = 1 if name not in result else result[name] + 1

        return result


    ## BeautifulSoup section
    def __tag_visible__(self, element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def __text_from_html__(self, body):
        soup = BeautifulSoup(body, 'html.parser')
        texts = soup.findAll(text=True)
        visible_texts = filter(self.__tag_visible__, texts)  
        return u" ".join(t.strip() for t in visible_texts)
    
if __name__ == '__main__':
    tokenizer = Tokenizer(3, 25)
    print(tokenizer.get_tokens_with_frequency("td257160km prueba² prueba corto žarnićli"))