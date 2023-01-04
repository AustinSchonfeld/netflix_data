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

#now lets explode the lists into individual rows associated with the proper show_id

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
#there are too many categories to do a single grouped bar chart, lets do a different chart for each category
unstacked_ratings.plot(kind='bar')
plt.savefig(('genres_and_ratings.png'))