#!/usr/bin/python2

from Crypto.Cipher import AES
import hashlib
import numpy as np
import pandas as pd

#setup function for first time launch (making dataframe)
def firstLaunch():
    print("\nWelcome")
    categories = raw_input("\nWhat categories would you like to have? (example: instock,colour,modelnum,serialnum)\n>>> ")
    categories = categories.split(",")

    print("\nWhat items would you like to add?")
    items = raw_input("Please start each item with a name then fill in all categoires then seperate items with colons (example: soap,3,blue,A1822,F0123ws:shampoo,3,red,A122,DASasd3)\n>>> ")
    items = items.split(":")
    for i in range(len(items)):
        items[i] = items[i].split(",")
    items = np.array(items)
    
    try:
        inventory = pd.DataFrame(items[:,1:], index = items[:,0], columns = categories)
        return(inventory)
    except:
        print("\n[!] The amount of categories did not match the data provided")
        firstLaunch()

#Every launch after the first one ... turns string into dataframe
def secondaryLaunches(inventory):
    #remove checkPhrase and padding
    inventory = inventory.split("@")
    del inventory[0]
    del inventory[1]

    #organize list into 2d with [0] being data and [1] being list of item names
    inventory = inventory[0].split(";")
    inventory[0] = inventory[0].split(":")
    inventory[1] = inventory[1].split(",")

    #separate data into lists
    for i in range(len(inventory[0])):
        inventory[0][i] = inventory[0][i].split(",")

    #remove empty string from end of lists
    del inventory[1][-1]
    del inventory[0][-1]
    for i in range(len(inventory[0])):
        del inventory[0][i][-1]

    #turn data into numpy array then combine with names to make dataframe
    data = np.array(inventory[0])
    inventory = pd.DataFrame(data[1:], index = inventory[1], columns = data[0])
    return(inventory)

#setting up encryptor and decryptor
def setupEncryption():
    key = raw_input("\nWhat is your password?\n>>> ")
    key2 = raw_input("\nPlease confirm your password:\n>>> ")
    while key != key2:
        print("\n[!] Cofirmation did not match first password please re-enter")
        key = raw_input("\nWhat is your password?\n>>> ")
        key2 = raw_input("\nPlease confirm your password:\n>>> ")
    print("\n[*] Trying to decrypt files with that passcode")
    key = hashlib.sha256(key).digest()
    mode = AES.MODE_CBC
    IV = "\x00"*16
    encryptor = AES.new(key, mode, IV=IV)
    decryptor = AES.new(key, mode, IV=IV)
    return([encryptor,decryptor])

#decrpyting file
def decryptFile(cryptors):
    inventoryfile = open("inventory.txt", "r")
    inventory = inventoryfile.read()
    inventory = cryptors[1].decrypt(inventory)
    inventoryfile.close()
    return(inventory)

#encrypting data and writing encrypted data to file
def encryptingFile(inventory, cryptors):
    checkPhrase = "goodtogogoodtogo@"
    allItems = inventory.index.values.tolist()

    #Building 2d array of dataframe
    colms = [[]]
    colNames = inventory.columns.get_values().tolist()
    for colm in colNames:
        colms[0].append(colm)
    temp = inventory.values.tolist()
    inventory = colms
    for i in temp:
        inventory.append(i)

    #turning items and inventory to string
    invStr = ""
    for r in inventory:
        for c in r:
            invStr += (c + ",")
        invStr += ":"

    invStr += ";"
    for i in allItems:
        invStr += (i + ",")
            
    #padding string then enrypting and writing to file
    inventory = checkPhrase + invStr
    inventory += "@"
    while (len(inventory)%16 != 0):
        inventory += "0"
    inventory = cryptors[0].encrypt(inventory)
    inventoryfile = open("inventory.txt", "w")
    inventoryfile.write(inventory)
    inventoryfile.close()
    return(None)

#********MAIN********

#Launch
cryptors = setupEncryption()
inventory = decryptFile(cryptors)

while inventory[:16] != "goodtogogoodtogo":
    print("\n[!] That key did not work please enter another")
    cryptors = setupEncryption()
    inventory = decryptFile(cryptors)

#check to see if it's first launch of program
if (inventory == "goodtogogoodtogo"):
    inventory = firstLaunch()
else:
    inventory = secondaryLaunches(inventory)

#Main interface
running = True
while (running == True):
    choice = raw_input("\nHow may I help you today?\n>>> ").lower()
    
    if (choice == "check"):
        choice = raw_input("\nWhat is the name of the item you want to check?\n>>> ")
        try:
            print(inventory.loc[[choice]])
        except:
            print("\nSorry I can't find that item.")
    
    elif (choice == "change"):
        item = raw_input("\nWhat item would you like to change?\n>>> ")
        cat = raw_input("\nWhat category would you like to change?\n>>> ")
        new = raw_input("\nWhat is the new value?\n>>> ")
        inventory.set_value(item, cat, new)
        print("\n[*] Item value changed")
    
    elif (choice == "remove item"):
        item = raw_input("\nWhat item would you like to remove?\n>>> ")
        try:
            inventory = inventory.drop(item)
            print("\n[*] Item removed")
        except:
            print("\n[!] That item could not be found and so was not removed")
    
    elif (choice == "remove category"):
        cat = raw_input("\nWhat category would you like to remove?\n>>> ")
        try:
            inventory = inventory.drop(cat, 1)
            print("\n [*] Category removed")
        except:
            print("\n[!] That category could not be found and so was not removed")
    
    elif (choice == "add item"):
        item = raw_input("\nWhat is the new item you would like to add?\n>>> ")
        cats = []
        for i in inventory.columns.get_values().tolist():
            value = raw_input("\nEnter item's value for " + i + "\n>>> ")
            cats.append(value)
        inventory.loc[item] = cats
        print("\n[*] Item added")
    
    elif (choice == "add category"):
        cat = raw_input("\nWhat is the name of the category would you like to add?\n>>> ")
        inventory[cat] = pd.Series(np.random.randn(), index=inventory.index)
        print("\n[*] Category added")
        
    elif (choice == "list"):
        print(inventory)
    
    elif (choice == "change password"):
        cryptors = setupEncryption()

    elif (choice == "save"):
        encryptingFile(inventory, cryptors)

    elif (choice == "exit"):
        #encrypt and write data to file
        encryptingFile(inventory, cryptors)
        running = False
    
    else:
        print("\n[!] Unknown command...")
