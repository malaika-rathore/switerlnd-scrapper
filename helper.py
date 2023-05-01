def check_companies_validation(valid_links,full_document,company):
    if (len(valid_links) >= 5):
        # throw("companies are more than 5")
        return False

    return company.get("name").lower().startswith(full_document.get("search_text").lower())