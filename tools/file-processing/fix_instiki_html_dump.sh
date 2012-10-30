find ./ -name "*.xhtml"  | xargs sed -i.bak -r -e "s/%([0-9A-Z]{2})/%25\\1/g"
