# run flask from index
if __name__ == '__main__':
    from index import app
    app.run(port=3000, debug=True)
