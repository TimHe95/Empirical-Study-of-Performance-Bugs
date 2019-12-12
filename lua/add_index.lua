#!/usr/bin/env sysbench

require("oltp_common")

function prepare_statements()
   prepare_add_index()
end

function event()
   execute_add_index()
end
