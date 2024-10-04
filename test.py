

import re



str1 = 'i have this [hehe] & (i dont)@#$%'
str2 = 'i don\'t got \tthis!'
str3 = '<danger><html></html>'
str4 = 'some\of\thes{e}, dumpers^^ \n'
str5 = 'its so #over, | its so back*.'

# re_clean_str = r'[\(\)\|\\\/\[\]\{\}\<\>]'
re_clean_str = r'[@#$%^&*`<>/{}\[\]|\\()\n\r\t]'

def clean(s):
    print(s)
    print(re.sub(re_clean_str, '', s))

clean(str1)
clean(str2)
clean(str3)
clean(str4)
clean(str5)