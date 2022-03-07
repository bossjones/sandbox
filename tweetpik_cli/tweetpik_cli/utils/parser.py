# https://stackoverflow.com/questions/9626535/get-protocol-host-name-from-url
# TODO: Use this for test data
# urls = [
# "http://stackoverflow.com:8080/some/folder?test=/questions/9626535/get-domain-name-from-url",
# "Stackoverflow.com:8080/some/folder?test=/questions/9626535/get-domain-name-from-url",
# "http://stackoverflow.com/some/folder?test=/questions/9626535/get-domain-name-from-url",
# "https://StackOverflow.com:8080?test=/questions/9626535/get-domain-name-from-url",
# "stackoverflow.com?test=questions&v=get-domain-name-from-url"]
def get_domain_from_fqdn(url: str) -> str:
    """Input a fqdn and get only the domain name back
    Arguments:
        url STR -- url string of a domain. Eg. http://stackoverflow.com:8080/some/folder?test=/questions/9626535/get-domain-name-from-url
    Returns:
        STR -- domain name in str format. Eg. stackoverflow.com
    """
    spltAr = url.split("://")
    i = (0, 1)[len(spltAr) > 1]
    dm = spltAr[i].split("?")[0].split("/")[0].split(":")[0].lower()
    return dm
