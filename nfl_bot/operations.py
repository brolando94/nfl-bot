import http.client


def send(message, webhook_url):
    # your webhook URL
    # compile the form data (BOUNDARY can be anything)
    formdata = "------:::BOUNDARY:::\r\nContent-Disposition: form-data; name=\"content\"\r\n\r\n" + message + "\r\n------:::BOUNDARY:::--"

    # get the connection and make the request
    connection = http.client.HTTPSConnection("discordapp.com")
    connection.request("POST", webhook_url, formdata.encode('utf-8'), {
        'content-type': "multipart/form-data; boundary=----:::BOUNDARY:::",
        'cache-control': "no-cache",
    })

    # get the response
    wh_response = connection.getresponse()
    result = wh_response.read()

    # return back to the calling function with the result
    return result.decode("utf-8")


def update(message, webhook_url):
    # your webhook URL
    # compile the form data (BOUNDARY can be anything)
    formdata = "------:::BOUNDARY:::\r\nContent-Disposition: form-data; name=\"content\"\r\n\r\n" + message + "\r\n------:::BOUNDARY:::--"

    # get the connection and make the request
    connection = http.client.HTTPSConnection("discordapp.com")
    connection.request("PATCH", webhook_url, formdata.encode('utf-8'), {
        'content-type': "multipart/form-data; boundary=----:::BOUNDARY:::",
        'cache-control': "no-cache",
    })

    # get the response
    wh_response = connection.getresponse()
    result = wh_response.read()

    # return back to the calling function with the result
    return result.decode("utf-8")