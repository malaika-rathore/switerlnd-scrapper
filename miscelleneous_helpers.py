def find_text(element,Selector,selector_value):
    try:
        return element.find_element(Selector,selector_value).text
    except Exception as e:
        return ""
    
def append_additional_detail(company,datatype,data):
    company.setdefault("additional_detail",[]).append({"type":datatype,"data":data})


def append_addresses(company,address_type,address):
    company.setdefault("address_detail",[]).append({"type":address_type,"address":address})

def append_people_detail(company,person):
    company.setdefault("people_detail",[]).append(person)