lst1=[(1.3, 2.4), (2.5,5.2)]
lst2=[(round(coord[0]), round(coord[1])) for coord in lst1]
print(lst2)