# -*- coding: utf-8 -*-

# Two arrays: one for languages, and another for frequencies. Each indice in the frequency 
# array corresponds to the respective language in the language array. The indexKey array is 
# a reference list for people reading the code base.
indexKey = ['English', 'Spanish', 'Russian']
languages = ["abcdefghijklmnopqrstuvwxyz", "aábcdeéfghiíjklmnñoópqrstuúüvwxyz", "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"] 
frequencies = [[.0834, .0154, .0273, .0414, .1260, .0203, .0192, .0611, .0671, .0023, .0087, .0424, .0253, .0680, .0770, 
                .0166, .0009, .0568, .0611, .0937, .0285, .0106, .0234, .0020, .0204, .0006],
               [.1172, .0044, .0149, .0387, .0467, .1372, .0036, .0069, .0100, .0118, .0528, .0070, .0052, .0011, .0524, 
                .0308, .0683, .0017, .0844, .0076, .0289, .0111, .0641, .0720, .0460, .0455, .0002, .0012, .0105, .0004, 
                .0014, .0109, .0047], 
               [.0764, .0201, .0438, .0172, .0309, .0875, .0020, .0101, .0148, .0709, .0121, .0330, .0496, .0317, .0678, 
                .1118, .0247, .0423, .0497, .0609, .0222, .0021, .0095, .0039, .0140, .0072, .0030, .0002, .0236, .0184, 
                .0036, .0047, .0196]]

# This is a check to make sure that the message or key is actually in the language chosen.
def langCheck(p, lang):
    for ele in p:
        if ele not in languages[lang]:
            return False
    return True
        

# This is the encrypting function. It takes a message 'm', a key 'k', and a index number 'lang'. This function basically
# performs the Caesar cipher shift on a rotating basis based on the key that is signature to the Vigenere cipher.
def encrypt(m, k, lang):
    c = ""
    kpos = [] # return the index of characters ex: if k='d' then kpos= 3
    for x in k:
        kpos.append(languages[lang].find(x)) # Searches the specific alphabet for the index of each letter in the key.
    i = 0
    for x in m:
      if i == len(kpos): # Rotaties the letter from the key that is used.
          i = 0
      pos = languages[lang].find(x) + kpos[i] # Finds the index of the letter and performs the shift with the respective letter from the key.
      if pos > len(languages[lang]) - 1: # We use len(languages[lang]) to make sure it is modular depending on language.
          pos = pos - len(languages[lang])  # If we exceed the length of the alphabet, we wrap around the alphabet's indexing.
      c += languages[lang][pos].capitalize()  # Cipher text always has to be capitalized :3
      i +=1
    return c

# This is the basic decrypting function. I wanted the program to be modular based on whether you had the key or not, so I added this function
# for when you had the key in the beginning. Furthermore, this function is also used in the other decrypting function, but I kept it separate
# again for more options in the initial input phase. 
def decrypt(c, k, lang):
    p = ""
    kpos = []
    for x in k:
        kpos.append(languages[lang].find(x)) # Find index value for each letter in key.
    i = 0
    for x in c:
      if i == len(kpos): # Rotates the letter from the key that is used.
          i = 0
      pos = languages[lang].find(x.lower()) - kpos[i] # For each letter in the cipher, finds the corresponding letter by undoing the Caesar shift.
      if pos < 0:
          pos = pos + len(languages[lang]) # Makes sure to wrap the index around if the current index value is negative from the Caesar undo.
      p += languages[lang][pos].lower()
      i +=1
    return p

# This is where things get both very interesting and difficult. When we went over the Vigenere cipher in the book, we did something special to find
# the length of the key. We rotated the cipher text some number of times and found the number of coincidences. The value that is highest is most
# likely the key length. The way I implemented this was to use a substring and a superstring that was a slice of the original cipher text based on
# what key length we are testing. Since we don't care about checking either end of the string, slicing works because it gets rid of the excess. That
# way, we can just compare each index to count coincidences since the sub and super string will always be the same length. We then put each
# (key length, coincidences) pair in a dictionary, and then sort it. Since sometimes a multiple of the actual key length comes up as the value 
# (such as 15 instead of 5), we do a check on the first and second guesses and take the lower value. However, later, this proved to be not enough
# of a check, so I implemented another method in a later function. 
def findKeyLength(c, lang):
    coincidenceTable = {}
    for i in range(1, 17):
        coincidences = 0

        sub = c[:len(c)-i] # Substring that cuts off the first 'i' letters
        sup = c[i:] # Superstring that cuts off the last 'i' letters
        for j in range(len(sub)):
            if sub[j] == sup[j]:
                coincidences += 1
        coincidenceTable[i] = coincidences
    sortedTable = sorted(coincidenceTable.items(), key = lambda x: x[1],reverse = True) # Sorts the tuples in the dictionary by value.
    best = sortedTable[0][0]
    second = sortedTable[1][0]
    # print('\n', sortedTable)
    if best % second == 0: # Comparison of the best and second guess to see if the second best is a multiple of the best
     return second
    else:
     return best


# This function is to find the actual key now that we have the length from the above function. To do this, I am applying the methods from our book 
# to create frequency vectors for n substrings, where n is the length of the key. To create these substrings, I am slicing the cipher text by using
# a step of length 'n' and starting with each index less than 'n'. Suppose n = 5. Then I will create 5 substrings with the first one containing the
# letters at index 0, 5, 10, ... and the second one containing 1, 6, 11, ... with the last containing 4, 9, 14, ... After this, we find the
# frequency of each letter in each substring. Then we find the dot product of each letter in the alphabet by multiplying the respective substring's
# frequency vector by the alphabet's relative frequency. We rotate the alphabet's vector depending on what letter it is, so when we find the
# maximal dot product, we can reasonably conclude that as the letter for this substring. 
def findKey(c, n, lang):
    freq = frequencies[lang] 
    alpha = languages[lang]
    key = []
    for i in range(n): # For each letter in the key
        sub = c[i::n] # Create a substring of every 'n' letter from 'i' in the cipher text
        freqVec = []
        letter = 0
        maxDot = 0
        for j in range(len(alpha)): # For each letter in the alphabet
            count = 0
            for k in range(len(sub)): # For each letter in the substring
                if alpha[j] == sub[k].lower(): # Count how many times the 'j' letter appears in the sub string
                    count += 1
            freqVec.append(count)
        for x in range(len(alpha)): # For each letter in the alphabet
            freqRot = freq[-x:] + freq[:-x] # Create a new comparison vector based on the letter's index
            dotProd = sum(x_i*y_i for x_i, y_i in zip(freqVec, freqRot)) # Find the dot product of the two frequency vectors.
            if dotProd > maxDot: # If the new dot product is bigger than the saved one, update the letter and maxDot variables.
                letter = x
                maxDot = dotProd
        key.append(alpha[letter])
    #print('\n', key)
        
    # Since the key length still might actually be too long, and the word repeated once or twice, the following 
    # is a test to see whether or not the word repeats in our current key. If it does, it will slice the key
    # to the proper length. The way it does this is by checking if a number from 2 to the length of the key is a multiple of the length of the 
    # current key. If it is, it creates substrings based on the multiple and places the first letter of each potential word in one substring, the
    # second in another, etc. until the last letter. For example, if currently, the key is:
    # ['p','e','r','r','o','p','e','r','r','o','p','e','r','r','o']
    # it will make 5 substrings of:
    # ['p','p','p'], ['e','e','e'], ['r','r','r'], ['r','r','r'], ['o','o','o']
    # It will then compare to see if all the letters are the same in each substring. If this is true, it will then slice the key to keep only the
    # first n letters. Thus, the new key will be:
    # ['p','e','r','r','o']
    for y in range(2, len(key)): # Assuming the key is longer than 1, which is a slight restriction. I still have to put tests in the inputs. 
        repeat = True
        if len(key) % y == 0:
            for z in range(len(key)//y):
                sub = key[z::y]
                #print(sub)
                repeat = all(elem == sub[0] for elem in sub)
        else:
            repeat = False
        if repeat:
            key = key[:y]
    #print(key)
    return key


# This function is a grouping function to run all of my other functions in. This way, when running my main program,
# I keep everything neat and tidy and only have to keep track of the input variables.
def decryptNoKey(c, lang):
    n = findKeyLength(c, lang)
    key = findKey(c, n, lang)
    k = ''
    for letter in key: # Concatenate all the letters in the array to form a key string.
        k += letter 
    m = decrypt(c, k, lang)
    return (m,k)
    
try:
    langInput = input("\nWelcome to Dhruva's Vigenere Cypher Program!\n\n"
          '''When using the program, please make sure that the text message contains only characters and is all lowercase.
          \nAlso make sure the key is one character word!\n\n'''
          "Please enter the number corresponding to your language of choice!\nEnglish: 0\nSpanish: 1\nRussian: 2\n\nChoice: ")
    if not all(char.isdigit() for char in langInput):
        print('\nNot a valid language choice! Numbers only!')
    else:
        lang = int(langInput)
        if lang >= len(languages):
            print('Not a valid language choice!')
        else: 
            choose = input("Type e to Encrypt a message \nType d to Decrypt a message \n\nChoice: ")
            if choose == 'e':
                m = input("Please enter the plain text: ")
                m = m.replace(" ", "")  # Makes sure there are no spaces
                if not langCheck(m, lang):
                    if any(char.isdigit() for char in m):
                        print("\nOnly letters please!")
                    print("\nPlease enter the chosen language for the message!")
                elif m.isalpha():
                    k = input("Enter the key.\nPlease make sure it is between 2 and 16 characters long: ")
                    k = k.strip()  # Removes possible white space.
                    if not langCheck(k, lang):
                        if any(char.isdigit() for char in m):
                            print("\nOnly letters please!")
                        print("\nPlease enter the chosen language for the key!")
                    elif len(k) < 2 or len(k) > 16:
                        print("\nNot a valid key length!")
                    elif k.isalpha():
                        c = encrypt(m, k, lang)
                        print("\nThe cipher text is:\n\n" + c)
                    else:
                        print(k)
                        print("\nEnter valid key, key is only one character word!")
            elif choose == 'd':
                c = input("Enter the cipher text: ")
                c = c.replace(" ", "")
                if not langCheck(c, lang):
                    if any(char.isdigit() for char in m):
                        print("\nOnly letters please!")
                    print("\nPlease enter the chosen language for the cipher!")
                elif c.isalpha():
                    key = input("Do you have the key?\nEnter 'y' for yes and 'n' for no: ")
                    if key == 'y':
                        k = input("Enter the key: ")
                        if not langCheck(k, lang):
                            if any(char.isdigit() for char in m):
                                print("\nOnly letters please!")
                            print("\nPlease enter the chosen language for the key!")
                        elif not k.isalpha():
                            print("\nPlease enter a valid key of only one character word!")
                        else:
                            m = decrypt(c, k, lang)
                            print("\nThe plain text is:\n\n" + m)
                    elif key == 'n':
                        print("\nOh no! That's okay though! We can find the key with MATH! Just wait one moment!")
                        m = decryptNoKey(c, lang)
                        print("\nThe plain text is:\n\n" + m[0])
                        print("\nThe secret word was:\n\n" + m[1])
                    else:
                        print("\nYes or no, please!")
                else:
                    print("\nOnly letters are allowed!")
            else:
                print("\nPlease enter a valid choice!")
except Exception as e:
    print(e)
    exit("\nEnter a valid text please!")