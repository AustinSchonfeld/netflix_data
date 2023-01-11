import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

#import the csv into a dataframe
data = pd.read_csv('netflix_titles.csv', encoding = 'utf-8')

#for titles with no country value, replace nan with "none"
data.country.fillna('None', inplace = True)
#if a country cell has multiple values, make those values into a list
data.country = list(data.country.str.split(','))

#in case country data has extra whitespace use map() and a remove_whitespace function to apply the strip() function to each value in the list for each cell
#remove_whitespace loops through each item in the cell list and removes extra whitespace
def remove_whitespace(cell):
    new_list = []
    for item in cell:
        new_list.append(item.strip())
    return new_list

#remove_whitespace is applied to each list in each cell using the map() function
data["country"] = data["country"].map(lambda x:remove_whitespace(x))

#fill in na values for director and cast
data.director.fillna('no data', inplace = True)
data.cast.fillna('no data', inplace = True)
#lets also turn directors, cast, and listed_in into lists
data.director = list(data.director.str.split(','))
data.cast = list(data.cast.str.split(','))
data.listed_in = list(data.listed_in.str.split(','))

#lists within cells need to go, let's break down the data into several dataframes using the show_id
def breakdown(column):
    new_frame = data[['show_id', column]]
    return new_frame

#use the breakdown function to get tables for each column
types = breakdown('type')
titles = breakdown('title')
directors = breakdown('director')
cast = breakdown('cast')
country = breakdown('country')
dates = breakdown('date_added')
releases = breakdown('release_year')
ratings = breakdown('rating')
durations = breakdown('duration')
categories = breakdown('listed_in')
descriptions = breakdown('description')

#now lets explode the lists into individual rows associated with the proper show_id in order to get rid of the lists within cells

directors = directors.explode('director')
cast = cast.explode('cast')
country = country.explode('country')
categories = categories.explode('listed_in')

#now that everything is organized into dataframes with primary ids, lets do some analysis
#first I'd like to know the distribution of movie and show lengths across Netflix
#movies and shows will need to be separated and then their length converted to an int
#merge the types and durations dataframes
types_durations = types.merge(durations, on='show_id')
#split the movies and shows
movie_durations = types_durations[types_durations.type == 'Movie']
show_durations = types_durations[types_durations.type == 'TV Show']
#split the min/seasons descriptor from the duration
movie_durations.duration = movie_durations.duration.str.split(' ')
show_durations.duration = show_durations.duration.str.split(' ')
#drop na values for duration
movie_durations.dropna(inplace = True)
show_durations.dropna(inplace = True)
#pick the numerical value from the list
movie_durations.duration = movie_durations.duration.map(lambda x: x[0])
show_durations.duration = show_durations.duration.map(lambda x: x[0])
#convert strings to int values
movie_durations.duration = movie_durations.duration.astype('int')
show_durations.duration = show_durations.duration.astype('int')
#graph charts of movie lengths and tv show seasons
f = plt.figure()
f.set_figwidth(20)
f.set_figheight(10)
plt.hist(movie_durations.duration, bins = [*range(0, 200, 10)], edgecolor = 'black')
plt.xticks([*range(0, 200, 10)])
plt.title('Distribution of Movie Lengths')
plt.xlabel('Movie Length (mins)')
plt.ylabel('Number of Movies')
plt.savefig('movie_lengths.png')
plt.clf()

#need value counts for # of seasons
labels, counts = np.unique(show_durations.duration, return_counts=True)
f = plt.figure()
f.set_figwidth(20)
f.set_figheight(10)
plt.bar(labels, counts, edgecolor = 'black')
plt.xticks(labels)
plt.title('Distribution of # of Seasons for TV Shows')
plt.xlabel('Number of Seasons')
plt.ylabel('Number of Shows')
plt.savefig('show_lengths.png')
plt.clf()

#lets get the distribution of ratings for each genre
#combine ratings with categories
ratings_by_genre = ratings.merge(categories, on = 'show_id')
#remove the typos that the code on line 110 reveals
ratings_by_genre = ratings_by_genre.drop(ratings_by_genre[(ratings_by_genre.rating == '66 min') | (ratings_by_genre.rating == '74 min') | (ratings_by_genre.rating == '84 min')].index)
#now to get the number of shows per rating per category
ratings_by_genre = ratings_by_genre.groupby(['listed_in', 'rating']).rating.count()
#unstack the data into a more usable table
unstacked_ratings = ratings_by_genre.unstack()
#unstacked data revealed some typos where there is a movie duration in place of a rating, go back above and remove the rows containing 66, 74, and 84 min for ratings
print(unstacked_ratings.head(20))
#there are too many categories to do a single grouped bar chart, lets do a single example chart of one category
comedy_ratings = unstacked_ratings.loc['Comedies']
comedy_ratings = comedy_ratings.reindex(index = ['G', 'PG', 'PG-13', 'R', 'NC-17', 'TV-G', 'TV-PG', 'TV-14', 'TV-MA', 'TV-Y', 'TV-Y7', 'TV-Y7-FV', 'UR', 'NR'])
comedy_ratings.plot(kind = 'bar')
plt.xlabel('Movie/Show Rating')
plt.ylabel('Number of Movies/Shows')
plt.title('Distribution of Movie and Show Ratings for Comedies')
plt.savefig('comedy_ratings.png')
plt.clf()

#How much of Netflix's content is recently released and how much is older movies/shows?
releases.release_year = releases.release_year.astype('int')
labels, counts = np.unique(releases.release_year, return_counts = True)
plt.bar(labels, counts, edgecolor = 'black')
plt.title('Original Release Dates of Netflix Content')
plt.xlabel('Year Released')
plt.ylabel('Number of Movies/Shows')
plt.savefig('release_years.png')

### NEW TASK ###
### Create a search function based on user input ###

#main menu function
def main_menu():
    print('Welcome to Netflix Search 1.0')
    print('''Please select a search mode or press 5 to end program:
    1) Title
    2) Actor
    3) Director
    4) Category
    5) Exit''')

#function that determines the search mode and determines if program should exit based on user input
def search_mode(mode):
    if mode == 1:
        print('Enter a title to search for:')
    elif mode == 2:
        print('Enter an actor to search for:')
    elif mode == 3:   
        print('Enter a director to search for:')
    elif mode == 4:
        print('Enter a category to search for:')
    else:
        print('You have entered an invalid search mode. Please try again.')
        mode = check_input()
    return mode

#function that displays search results
def search_results(mode, search):
    results = None
    if mode == 1:
        print('Title Results for: ' + search)
    elif mode == 2:
        print('Actor Results for: ' + search)
    elif mode == 3:
        print('Director Results for: ' + search)
    elif mode == 4:
        print('Category Results for: ' + search)    

#function that asks the user if they would like to return to main menu
def return_to_main():
    print('Would you like to return to main menu? (y/n)')
    main = input()
    return main

#function that takes user input and checks if its numeric
def check_input():
    end_function = False
    while end_function == False:
        user_input = input()
        if ((user_input.isnumeric()) & (len(user_input) == 1) & (int(user_input) <= 5)):
            end_function = True
            output = int(user_input)
        else:
            end_function = False
            print('Please input a number (1-5)')
    return output

exit = False

#main code block for user search
#as long as user does not want to exit, code keeps looping
while exit == False:
    #print main menu
    main_menu()
    #ask for user input on search mode
    mode = check_input()
    #determines if program should exit based on user input at main menu
    if mode == 5:
        print('Goodbye')
        exit = True
        continue
    #if user does not exit, ask for search parameters and print results
    else:
        search_mode(mode)
        user_search = input()
        search_results(mode, user_search)
        #after printing results, ask user if they would like to return to main menu
        main = 'failure'
        while ((main != 'y') & (main !='n')):
            main = return_to_main()
            if main == 'y':
                continue
            #if 'n' program exits
            elif main == 'n':
                exit = True 
                continue 
            #check to see if user entered something other than 'y' or 'n'
            else:
                print('Please try input again')