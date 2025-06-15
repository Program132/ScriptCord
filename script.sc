config COMMAND
set COMMAND_NAME ""
set DESCRIPTION ""
set ALIASES ""
set GUILD ""

setl myLocalVar "Hello"

send "Hi" 4565461655646541 # format: 'send "<message>" <id channel>
react ":my_emoji:" 14654564564 # format: 'react "<emoji code>" <id msg>
role:add 156165146541 5456456464114 # format: 'role:<add or remove> <member id> <role id>

embed:create embedName
embed:conf embedName "My Title" "My URL" "My Desc" "My Color"
embed:set_author embedName "Name" "URL" "Icon URL"
embed:set_thumbails embedName "URL"
embed:add_l embedName "Title" "Value"
embed:add_nl embedName "Title" "Value"
embed:set_footer embedName "Text blbalblabla"
embed:send embedName 4546545648979165156