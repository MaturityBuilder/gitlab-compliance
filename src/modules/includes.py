import modules.yaml_md_table as gldocs
def document_includes():
    print("Generating Documentation for Includes")
    import yaml
    from pytablewriter import MarkdownTableWriter
    with open('/gitlab-project/.gitlab-ci.yml', 'r') as file:
        try:
            data = yaml.load(file, Loader=yaml.SafeLoader)
            includes = data["include"]
            # print(gldocs.generate_markdown_table(includes))
            from prettytable import PrettyTable
            includes_table = PrettyTable()
            includes_table.field_names = ["Include Type", "Project/File", "Version", ""]
            # includes_table.add_rows([includes])

            for i in includes:
                # type = i.keys
                if (type(i)) is dict:
                    print(i.keys())
                    if i.keys() == "dict_keys(['local'])":
                        Type = "Local"
                        print(Type)
            # print(includes_table)
        except yaml.YAMLError as exc:
            print(exc)



# def get_include_type(include_entry):

