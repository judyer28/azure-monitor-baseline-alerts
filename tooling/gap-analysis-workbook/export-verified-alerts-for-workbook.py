import os
import yaml
import json
import argparse

# Parse command line arguments
def parseArguments():
  parser = argparse.ArgumentParser(description='This script will export the alerts.yaml files into files needed for Gap Analysis workbook.')
  parser.add_argument('-p', '--path', type=str, required=False, metavar='path', help='Path to services directory', default='../../services')
  parser.add_argument('-j', '--output-json', type=str, required=False, metavar='file', help='Output path to JSON file')
  args = parser.parse_args()

  return args

# Output the alerts to a JSON file
def outputToJsonFile(data, filename):
  typeListString = ""
  alertListString = ""
  for providerKey in data.keys():
    for typeKey in data[providerKey].keys():
      # Skip if there are no alerts for this resource type
      if len(data[providerKey][typeKey]) == 0:
        continue
      typeListString = typeListString + '"microsoft.' + providerKey.lower() + "/" + typeKey.lower() + '",'
      alertListString = alertListString + '"microsoft.' + providerKey.lower() + "/" + typeKey.lower() + '","'
      for alert in data[providerKey][typeKey]:
        alertListString = alertListString + str(alert['properties'].get('metricName')) + ","
      alertListString = alertListString.rstrip(',') + '",'

  typeListString = typeListString.rstrip(',')
  alertListString = alertListString.rstrip(',')
  # Write resource type list to a file
  with open("verifiedTypeList.txt", "w") as f:
    f.write(typeListString)
  # Write alert list to a file
  with open("verifiedAlertList.txt", "w") as f:
    f.write(alertListString)

def readYamlData(dir):

  # Walk the directory tree and load all the alerts.yaml files
  # into a list of dictionaries using the folder path as the structure
  # for the dictionary.
  data = {}
  for root, dirs, files in os.walk(dir):
    for file in files:
      if file == 'alerts.yaml':
        with open(os.path.join(root, file)) as f:
          # Get current folder name and parent folder name
          # to use as keys in the dictionary
          resourceType = os.path.basename(root)
          resouceCategory = os.path.basename(os.path.dirname(root))

          if not resouceCategory in data:
            data[resouceCategory] = {}

          if not resourceType in data[resouceCategory]:
            data[resouceCategory][resourceType] = []

          alerts = yaml.safe_load(f)
          if alerts:
            for alert in alerts:
              if ('verified' in alert) and (alert['verified'] == False):
                continue
              if ('visible' in alert) and (alert['visible'] == False):
                continue
              if ('type' in alert) and (alert['type'] != 'Metric'):
                continue
              data[resouceCategory][resourceType].append(alert)

  return data

def main():

  args = parseArguments()

  data = readYamlData(args.path)

  if args.output_json:
    outputToJsonFile(data, args.output_json)

if __name__ == '__main__':
  main()
