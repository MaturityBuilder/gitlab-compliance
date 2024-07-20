import modules.yaml_md_table as gldocs
def document_includes(GLDOCS_CONFIG_FILE, WRITE_MODE="a"):

    print("Generating Documentation for Includes")
    import yaml
    from pytablewriter import MarkdownTableWriter
    from prettytable import MARKDOWN
    with open(GLDOCS_CONFIG_FILE, 'r') as file:
        try:
            data = yaml.load(file, Loader=yaml.SafeLoader)
            includes = data["include"]
            # print(gldocs.generate_markdown_table(includes))
            from prettytable import PrettyTable

            includes_table = PrettyTable()
            includes_table.set_style(MARKDOWN)
            includes_table.field_names = ["Include Type", "Project", "Version", "File", "Variables", "Rules"]
            # includes_table.add_rows([includes])
            print(includes)

            for i in includes:

                if isinstance(i, (str)):
                    print(i)
                    i = {"local": i}
                print(i)
                for key in i.keys():
                    type = key
                    print("Type is: " + key)
                    if type == "project":
                        # print("Type is: " + key)
                        version = i["ref"]
                        value   = i["project"]
                        file   = i["file"]
                        inc_vars = ""
                        try:
                            inc_vars = i["variables"]
                        except:
                            print("No Inputs found")
                        inc_rules = ""
                        try:
                            inc_rules = i["rules"]
                        except:
                            print("No rules found")
                        includes_table.add_row([type, value, version, file, inc_vars, inc_rules])

                    elif type == "component":
                        # print("Type is: " + key)
                        version = i["component"].split("@")[1]
                        value   = i["component"].split("@")[0]
                        inc_vars = ""
                        try:
                            inc_vars = i["inputs"]
                        except:
                            print("No Inputs found")

                        inc_rules = ""
                        try:
                            inc_rules = i["rules"]
                        except:
                            print("No rules found")
                        includes_table.add_row([type, value, version, "", inc_vars, inc_rules])
                    elif type == "local":
                        version = "n/a"
                        value = i[key]
                        inc_vars = ""
                        try:
                            inc_vars = i["variables"]
                        except:
                            print("No Variables found")

                        inc_rules = ""
                        try:
                            inc_rules = i["rules"]
                        except:
                            print("No rules found")
                        includes_table.add_row([type, value, version, "", inc_vars, inc_rules])
                        if type == "local" :
                            SUB_GLDOCS_CONFIG_FILE = "/gitlab-project/" + i[key]
                            try:
                                document_includes(GLDOCS_CONFIG_FILE=SUB_GLDOCS_CONFIG_FILE,WRITE_MODE="a")
                            except:
                                print("include don't exist in " + GLDOCS_CONFIG_FILE)

        except yaml.YAMLError as exc:
            print(exc)
        print("")
        print(str(includes_table))
        print("")

        GLDOCS_CONFIG_FILE_HEADING = str("## " + GLDOCS_CONFIG_FILE + "\n\n")
        f = open("GITLAB_CONFIGURATION.md", "a")
        f.write("\n\n")
        f.write(GLDOCS_CONFIG_FILE_HEADING)
        f.write(str(includes_table))
        f.close()
#open and read the file after the appending:




# def get_include_type(include_entry):

