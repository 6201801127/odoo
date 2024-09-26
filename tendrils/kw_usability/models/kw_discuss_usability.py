import datetime
import calendar
from odoo import models, fields, api


class kw_discuss_usability(models.Model):
    _name = "kw_discuss_usability"
    _description = "Discuss usability"
    _rec_name = "date"
    _order = "date asc"

    date = fields.Date("Date")
    no_of_user = fields.Integer(string='No. Of Users Logged In', )
    users_participated = fields.Integer(string='Users Participated In Chat', )
    direct_message = fields.Integer(string='Direct Message', )
    group_message = fields.Integer(string='Group Message', )
    total_message = fields.Integer(string='Total Message', )
    groups_created = fields.Integer(string='Total Groups Created', )
    total_active_groups = fields.Integer(string='Total Active Groups', )
    most_active_member = fields.Char(string='Most Active Member')
    most_active_group = fields.Char(string='Most Active Group')

    @api.model
    def action_search_usability(self, vals):
        month_dict = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9,
                      'Oct': 10, 'Nov': 11, 'Dec': 12}
        year = int(vals['year'])
        month = month_dict[vals['month']]
        lastday = calendar.monthrange(year, month)[1]
        ld = str(datetime.date(year, month, lastday))
        fd = str(datetime.date(year, month, 1))

        self._cr.execute("WITH DATERANGE AS \
                        (\
                                SELECT DATE(DATE) FROM generate_series('" + fd + "' :: DATE, '" + ld + "' :: DATE , '1 day') AS DATE\
                        ), TotLogin AS\
                        (\
                                select date(date_time), count(distinct user_id) as total_login\
                                from user_login_detail ul inner join res_users ru on ul.user_id = ru.id group by date(date_time)), msg as \
                                ( \
                               select date(date) as msgdate, \
                                count(distinct author_id) As total_active_user,sum(case when channel_type='chat' then 1 else 0 end) as total_direct_message, \
                                sum(case when channel_type='channel' then 1 else 0 end) as total_group_message, \
                                count(mm.id) as total_message \
                                from res_users ru join mail_message mm on ru.id = mm.create_uid \
                                join mail_channel mc on mc.id=mm.res_id \
                                where extract(year from date) = '" + vals['year'] + "' and to_char(date,'Mon') = '" +
                         vals['month'] + "' and mm.model='mail.channel' and mm.message_type = 'comment' and ru.password <> '' \
                                group by date(date) \
                        ),group_created as \
                        ( \
                                select date(mc.create_date) as crDate, count(mc.id) TotChannelCreated \
                                from res_users ru join mail_channel mc on ru.id = mc.create_uid \
                                where channel_type='channel' and ru.password <> '' \
                                group by date(mc.create_date) \
                        ),tot_Activegroups as \
                        ( \
                               select date(mm.create_date) as AGDate, count(distinct mc.id) AS TotActiveGroups \
                                from res_users ru join mail_message mm on ru.id = mm.create_uid \
                                join mail_channel mc on mc.id=mm.res_id \
                                where channel_type='channel' and ru.password <> ''  and mm.message_type = 'comment' \
                                group by date(mm.create_date) \
                        ),most_activeMember as \
                        ( \
                             with a as \
                                ( \
                                        select date(date) AS DATE, author_id, count(mm.id) as Totchart \
                                        from res_users ru join \
                                        mail_message mm on ru.id = mm.create_uid \
                                        join mail_channel mc on mc.id=mm.res_id \
                                        where model='mail.channel' and message_type = 'comment' and channel_type='chat' and ru.password <> '' \
                                        group by date(date), author_id \
                                ), b as \
                                ( \
                                        select date, max(Totchart) as MaxNoChat \
                                        from ( \
                                                select date(date) AS DATE, author_id, count(mm.id) as Totchart \
                                                from res_users ru join mail_message mm on ru.id = mm.create_uid \
                                                join mail_channel mc on mc.id=mm.res_id \
                                                where model='mail.channel' and message_type = 'comment' and channel_type='chat' and ru.password <> '' \
                                                group by date(date), author_id \
                                        ) as foo \
                                        group by date \
                                ) \
                                SELECT a.date, string_agg(u.name, ', ') as name \
                                FROM A JOIN B ON A.DATE=B.DATE AND A.Totchart=B.MaxNoChat \
                                JOIN res_partner u on u.id=a.author_id \
                                group by a.date \
                                order by date asc \
                        ),most_activeGroup as \
                        ( \
                                with a as \
                                ( \
                                        select date(date) AS DATE, res_id, count(mm.id) as Totchart \
                                        from res_users ru join mail_message mm on ru.id = mm.create_uid \
                                        join mail_channel mc on mc.id=mm.res_id \
                                        where model='mail.channel' and message_type = 'comment' and channel_type='channel' and ru.password <> '' \
                                        group by date(date), res_id \
                                ), b as \
                                ( \
                                select date, max(Totchart) as MaxNoChat \
                                from ( \
                                                select date(date) AS DATE, res_id, count(mm.id) as Totchart \
                                                from res_users ru join \
                                                mail_message mm on ru.id = mm.create_uid \
                                                join mail_channel mc on mc.id=mm.res_id \
                                                where model='mail.channel' and message_type = 'comment' and channel_type='channel' and ru.password <> '' \
                                                group by date(date), res_id \
                                        ) as foo \
                                        group by date \
                                ) \
                                SELECT a.date, string_agg(u.name,',') as name \
                                FROM A JOIN B ON A.DATE=B.DATE AND A.Totchart=B.MaxNoChat \
                                JOIN mail_channel u on u.id=a.res_id group by a.date order by a.date asc \
                        ) \
                        SELECT DR.DATE, coalesce(TL.total_login, 0) AS total_login \
                        , coalesce(msg.total_active_user, 0) AS total_active_user \
                        , coalesce(msg.total_direct_message, 0) AS total_direct_message \
                        , coalesce(msg.total_group_message, 0) AS total_group_message \
                        , coalesce(msg.total_message, 0) AS total_message \
                        , coalesce(group_created.TotChannelCreated, 0) AS total_groupsCreated \
                        , coalesce(tot_Activegroups.TotActiveGroups, 0) AS total_active_groups \
                        , coalesce(most_activeMember.name,'NA') as most_activeMember \
                        , coalesce(most_activeGroup.name,'NA') as most_activeGroup \
                        FROM DATERANGE DR \
                        LEFT JOIN TotLogin TL ON DR.DATE=TL.DATE \
                        LEFT JOIN Msg ON DR.DATE=msg.msgdate \
                        LEFT JOIN group_created ON DR.DATE=group_created.crDate \
                        LEFT JOIN tot_Activegroups ON DR.DATE=tot_Activegroups.AGDate \
                        LEFT JOIN most_activeMember ON DR.DATE=most_activeMember.DATE \
                        LEFT JOIN most_activeGroup ON DR.DATE=most_activeGroup.DATE")
        result = self._cr.fetchall()
        # print(result)
        return result
