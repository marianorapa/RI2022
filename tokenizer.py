import re

class Tokenizer:
    def __init__(self, proper_name_splitting = False):
        self.PROPER_NAME_SPLITTING_ENABLED = proper_name_splitting  

    def __get_proper_names(self, line):
        #regex = "((?<!\A)(?<!(?:\.\s))(?:(?:(?:[A-Z][a-z]+)+)(?:[ ]*(?:[A-Z][a-z]+))*)[^\.])"        # Won't consider proper names after a ". " since it could mean the start of a sentence
        regex = "((?:(?:[A-Z](?:[a-z]+|\.+))+(?:\s[A-Z][a-z]+)+))"
        result = re.findall(regex, line)           
        return list(result) 
        
    def __is_date(self, token):
        regex = "(\d+[\/\.\-]\d+[\/\.\-]\d+)"
        return bool(re.match(regex, token))

    def __is_number(self, token):
        regex = "([\+\-]?(?:[0-9]+[,\-]?)*[0-9](?:[.][0-9]+)?)"     # accepts some form of telephone numbers and also numbers starting with + or -
        return re.findall(regex, token)

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

    def __translate(self, to_translate):
        tabin = u'áäâàãéëèêẽíïĩìîóõöòôúüùûũ'
        tabout = u'aaaaaeeeeeiiiiiooooouuuuu'
        tabin = [ord(char) for char in tabin]
        translate_table = dict(zip(tabin, tabout))
        return to_translate.translate(translate_table)

    def get_tokens_with_frequency(self, line):        
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

            result[token] = 1 if token not in result else result[token] + 1
        
        for name in proper_names_list:
            name = self.__remove_punctuation(name).lower()
            result[name] = 1 if name not in result else result[name] + 1

        return result