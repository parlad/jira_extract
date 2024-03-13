from jira import JIRA
import csv
import argparse

def main():
    parser = argparse.ArgumentParser(description='Calls a JQL query and exports it to a CSV file.\nWe suggest that the JQL queries end with "ORDER BY key"')
    parser.add_argument('-j','--jql', nargs='?', default='ORDER BY key', metavar='JQL_query', help='JQL query - default query is "ORDER BY key"')
    parser.add_argument('-u', required=True, metavar='username', help='Username')
    parser.add_argument('-p', required=True, metavar='password', help='Password')
    parser.add_argument('-n', nargs='?', default=1000, type=int, metavar='Number_of_issues', help='Number of issues per batch. Default of 1000 in line with Jira\'s default. For more details, check https://confluence.atlassian.com/jirakb/filter-export-only-contains-1000-issues-in-jira-server-191500982.html')
    parser.add_argument('-U','--url', required=True, metavar='Base_URL', help='Jira\'s base URL. For example, https://jira.mycompany.com')

    args = parser.parse_args()

    jql = args.jql
    username = args.u
    password = args.p
    step = args.n
    baseurl = args.url

    options = {
        'server': baseurl
    }

    try:
        jira = JIRA(options, basic_auth=(username, password))
    except Exception as e:
        print("Failed to connect to Jira:", e)
        return

    issues = jira.search_issues(jql, maxResults=step)

    if not issues:
        print("No issues found for the provided JQL query.")
        return

    output_filename = 'output.csv'

    with open(output_filename, 'w', newline='', encoding='utf-8') as output_file:
        csv_writer = csv.writer(output_file)

        # Write header
        header = ['Issue Key', 'Summary', 'Assignee', 'Reporter', 'Status']
        csv_writer.writerow(header)

        for issue in issues:
            assignee = getattr(issue.fields.assignee, 'displayName', 'Unassigned')
            reporter = getattr(issue.fields.reporter, 'displayName', 'Unknown')
            status = issue.fields.status.name

            row = [issue.key, issue.fields.summary, assignee, reporter, status]
            csv_writer.writerow(row)

    print("Data exported to:", output_filename)

if __name__ == "__main__":
    main()
