from selenium import webdriver
import time
DEBUG = True


def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


class SeleniumMod:
    def __init__(self, options: webdriver.ChromeOptions):
        self.max_tries = 3
        self.wait_time = 3
        self.cd = webdriver.Chrome()

    def click_by_xpath(self, xpath, element=None):
        result = False
        for i in range(self.max_tries):
            result = self.cd.execute_script(f"""
           //console.log(arguments);
            parent = document;
            if(arguments[1]){{
                parent = arguments[1];
            }}
            node = document.evaluate(arguments[0], parent, null,
            XPathResult.FIRST_ORDERED_NODE_TYPE, null ).singleNodeValue;
            //console.log(node);
            if(node){{
             node.scrollIntoView({{
            behavior: 'auto',
            block: 'center',
            inline: 'center'
            }});
             node.click(); 
             return true;
            }}
            return false;
                    """, xpath, element)
            if not result:
                time.sleep(self.wait_time)
            else:
                break
        return result

    def get_txt_by_xpath(self, xpath, element=None):
        value = ''
        for i in range(self.max_tries):
            value = self.cd.execute_script(f"""
           //console.log(arguments);
            parent = document;
            if(arguments[1]){{
                parent = arguments[1];
            }}
            //console.log(parent, 'parent');
            node = document.evaluate(arguments[0], parent, null,
            XPathResult.FIRST_ORDERED_NODE_TYPE, null ).singleNodeValue;
            //console.log(node, arguments);
            if(node){{
             node.scrollIntoView({{
             behavior: 'auto',
             block: 'center',
             inline: 'center'
             }});
             return node.innerText;
            }}
            return '';
            """, xpath, element)
            if value == '':
                time.sleep(self.wait_time)
        # debug_print(["get_txt_by_xpath", value])
        return value.strip()

    def get_e_by_xpath(self, xpath, element=None):
        e = None
        for i in range(self.max_tries):
            e = self.cd.execute_script(f"""
           //console.log(arguments);
            parent = document;
            if(arguments[1]){{
                parent = arguments[1];
            }}
            //console.log(parent, 'parent');
            node = document.evaluate(arguments[0], parent, null,
            XPathResult.FIRST_ORDERED_NODE_TYPE, null ).singleNodeValue;
            //console.log(node);
            return node != null?node: null;
            """, xpath, element)
            if e is None:
                time.sleep(self.wait_time)
        debug_print(["get_e_by_xpath", e])
        return e

    def get_attr_by_xpath(self, xpath: str, attr: str, element=None):
        value = ''
        for i in range(self.max_tries):
            value = self.cd.execute_script(f"""
           //console.log(arguments);
            parent = document;
            if(arguments[1]){{
                parent = arguments[1];
            }}
            //console.log(parent, 'parent');
            node = document.evaluate(arguments[0], parent, null,
            XPathResult.FIRST_ORDERED_NODE_TYPE, null ).singleNodeValue;
            //console.log(node);
            if(node){{
             node.scrollIntoView({{
             behavior: 'auto',
             block: 'center',
             inline: 'center'
             }});
             return node.getAttribute(arguments[2]);
            }}
            return '';
            """, xpath, element, attr)
            if value == '':
                time.sleep(self.wait_time)
        debug_print(["get_attr_by_xpath", value])
        return value.strip()