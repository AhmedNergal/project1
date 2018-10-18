# Library 2.0

## Contents

1. Introduction
1. Databases
1. User Registration
1. User Login
1. Searching
1. Book Page
1. Adding a Review
1. API
------------------------

### Introduction

Library 2.0 is a book review platform which holds in its database about 5000 books with information about their authors, publish date and ISBN numbers, the user has to be logged in to search for a certain book and get its data provided in the website's database along with additional data from Goodreads via the Goodreads API.

------------------------

### Databases

The application is connected to a database which consists of three tables:

1. Users Table
1. Books Table
1. Reviews Table

##### Users Table
The table contains the username and password for each registered user.

##### Books Table
The table contains the data for each book (ISBN, Title, Author, Publishing Year).

##### Reviews Table
The table consists of two foreign keys one for the user id and the other for the book id and a review title and a review body (Note that each user can only review a book once).

------------------------

### User Registration
Any user has to register for an account in order to use the website, so the user has to register using a unique username and password which will be saved in the users table in the database.

------------------------

### User Login
A user must be logged in order to access any of the website's services using his registered username and password, the user can logout to end their session.

------------------------

### Searching
Any logged in user will be redirected to the search page where they can search for a book using its ISBN, title, author's name, or its publishing year, the results will show up in the results page in the form of a table holding all of these data (Note that the search query is case-sensitive).

------------------------

### Book Pages
In the search results the user can click on a books name in order to access the book's page in the website, the book's page contains all the previously mentioned data in addition to extra data provided by Goodreads via the Goodreads API like the rating average and the total number of Goodreads reviews for the selected book, the user can also read reviews for the book written by another users, and they also can leave their own review for the book.

------------------------

### Adding a Review
By adding the "Add a Review" button on the book's page the user will be redirected to the review page where he can leave a rating (out of 5) and a review consisting of a review title and a review body.

------------------------

### API
Using the site's API users can get a book data in JSON form by its ISBN number using the API route
`/api/<isbn>`
