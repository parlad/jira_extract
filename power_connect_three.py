import requests
import csv
import argparse
import getpass

def main():
    parser = argparse.ArgumentParser(description='Calls a JQL query and exports it to a CSV file.\nWe suggest that the JQL queries end with "ORDER BY key"')
    parser.add_argument('-j', '--jql', nargs='?', default='ORDER BY key', metavar='JQL_query', help='JQL query - default query is "ORDER BY key"')
    parser.add_argument('-u', required=True, metavar='username', help='Username')
    parser.add_argument('-p', nargs='?', default='', metavar='password', help='Password. If parameter is not passed, the password will be prompted')
    parser.add_argument('-n', nargs='?', default=1000, type=int, metavar='Number_of_issues', help='Number of issues per batch. Default of 1000 in line with Jira\'s default. For more details, check https://confluence.atlassian.com/jirakb/filter-export-only-contains-1000-issues-in-jira-server-191500982.html')
    parser.add_argument('-U', '--url', required=True, metavar='Base_URL', help='Jira\'s base URL. For example, https://jira.mycompany.com')

    args = parser.parse_args()

    jql = args.jql
    username = args.u
    password = args.p
    step = args.n
    baseurl = args.url

    if password == '':
        password = getpass.getpass()

    output_filename = 'output.csv'

    url = f"{baseurl}/sr/jira.issueviews:searchrequest-csv-all-fields/temp/SearchRequest.csv?jqlQuery={jql}"
    start = 0
    total_issues_exported = 0

    try:
        with open(output_filename, 'w', newline='', encoding='utf-8') as output_file:
            csv_writer = csv.writer(output_file)

            while True:
                theurl = f"{url}&tempMax={step}&pager/start={start}"
                resp = requests.get(theurl, auth=(username, password), verify=False)
                resp.raise_for_status()  # Raise an exception for non-200 responses

                lines = resp.text.split('\n')
                if start == 0:
                    csv_writer.writerows([lines[0].split(',')])  # Write header only for the first batch

                for line in lines[1:]:
                    csv_writer.writerow(line.split(','))
                    total_issues_exported += 1  # Increment the total count for each issue exported

                start += step

                if len(lines) <= 1 or total_issues_exported % step != 0:  # If there are no more issues or the last batch is incomplete, break the loop
                    break

        print(f"All issues ({total_issues_exported}) exported")
        print("Data exported to:", output_filename)
    except requests.exceptions.RequestException as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
