

/********************************************************************************************************************************

*

*  Note moderator (/jscript/notemoderator.js)

*  Author: Krzysztof "Supryk" Supryczyński

*  Copyright: © 2013 - 2016 @ Krzysztof "Supryk" Supryczyński @ All rights reserved

*  

*  Website: 

*  Description: Allow moderator to add simple note to each post.

*

********************************************************************************************************************************/

/********************************************************************************************************************************

*

* This file is part of "Note moderator" plugin for MyBB.

* Copyright © 2013 - 2016 @ Krzysztof "Supryk" Supryczyński @ All rights reserved

*

* This program is free software: you can redistribute it and/or modify

* it under the terms of the GNU Lesser General Public License as published by

* the Free Software Foundation, either version 3 of the License, or

* (at your option) any later version.

*

* This program is distributed in the hope that it will be useful,

* but WITHOUT ANY WARRANTY; without even the implied warranty of

* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the

* GNU Lesser General Public License for more details.

*

* You should have received a copy of the GNU Lesser General Public License

* along with this program.  If not, see <http://www.gnu.org/licenses/>.

*

********************************************************************************************************************************/



var notemoderator = {

    

    init: function()

    {

        $(document).ready(function(){

        });

    },

    

    deletenote: function(pid, nmid)

    {

        $.prompt(lang.notemoderator_delete_confirm, {

            buttons:[

                    {title: yes_confirm, value: true},

                    {title: no_confirm, value: false}

            ],

            submit: function(e,v,m,f)

            {

                if(v == true)

                {

                    $.ajax(

                    {

                        url: "xmlhttp.php?action=deletenote&pid="+parseInt(pid)+"&nmid="+parseInt(nmid)+"&my_post_key="+my_post_key,

                        method: 'post',

                        async: true,

                        dataType: 'json',

                        complete: function(request)

                        {

                            var json = $.parseJSON(request.responseText);

                                

                            if(json.hasOwnProperty("errors"))

                            {

                                $.each(json.errors, function(i, message)

                                {

                                    $.jGrowl(lang.notemoderator_delete_error + ' ' + message);

                                });

                            }

                            else if(json.pid && json.nmid)

                            {

                                var pid = parseInt(json.pid);

                                var nmid = parseInt(json.nmid);

                                                                            

                                $('#notemoderator_'+nmid).slideToggle("slow", function()

                                {

                                    $('#notemoderator_'+nmid).remove();

                                    $.jGrowl(lang.notemoderator_has_been_deleted);

                                });

                            }

                            else

                            {

                                $.jGrowl(lang.unknown_error);

                            }

                        }

                    });

                }

            }

        });

    },

};



notemoderator.init();
