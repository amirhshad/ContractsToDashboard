import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    const resendApiKey = Deno.env.get('RESEND_API_KEY')

    if (!resendApiKey) {
      return new Response(
        JSON.stringify({ error: 'RESEND_API_KEY not configured' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    const supabase = createClient(supabaseUrl, supabaseServiceKey)

    // Get all users with email reminders enabled
    const { data: users, error: usersError } = await supabase
      .from('user_notification_preferences')
      .select('user_id, user:users(email, user_metadata)')
      .eq('email_reminders_enabled', true)

    if (usersError) throw usersError

    let emailsSent = 0

    for (const userPref of users || []) {
      const userEmail = userPref.user?.email
      const userName = userPref.user?.user_metadata?.display_name || 'there'
      
      if (!userEmail) continue

      // Get contracts with upcoming renewals in the next 60 days
      const { data: renewals, error: renewalsError } = await supabase
        .rpc('get_upcoming_renewals', {
          p_user_id: userPref.user_id,
          p_days: 60
        })

      if (renewalsError || !renewals?.length) continue

      // Group by reminder period
      const urgent = renewals.filter((r: any) => {
        const daysUntil = Math.ceil((new Date(r.next_renewal_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
        return daysUntil <= 7
      })

      const upcoming = renewals.filter((r: any) => {
        const daysUntil = Math.ceil((new Date(r.next_renewal_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
        return daysUntil > 7 && daysUntil <= 30
      })

      const later = renewals.filter((r: any) => {
        const daysUntil = Math.ceil((new Date(r.next_renewal_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
        return daysUntil > 30
      })

      // Build email content
      let html = `<h2>Hi ${userName}!</h2>`
      
      if (urgent.length > 0) {
        html += `<h3>⚠️ Urgent - Renewals this week</h3><ul>`
        for (const c of urgent) {
          html += `<li><strong>${c.provider_name}</strong> - ${c.contract_type} - $${c.monthly_cost}/${c.currency === 'USD' ? 'mo' : c.currency}</li>`
        }
        html += `</ul>`
      }

      if (upcoming.length > 0) {
        html += `<h3>📅 Coming up in 30 days</h3><ul>`
        for (const c of upcoming) {
          html += `<li><strong>${c.provider_name}</strong> - ${c.contract_type} - $${c.monthly_cost}/${c.currency === 'USD' ? 'mo' : c.currency}</li>`
        }
        html += `</ul>`
      }

      if (later.length > 0) {
        html += `<h3>📆 Later (60+ days)</h3><ul>`
        for (const c of later.slice(0, 5)) {
          html += `<li><strong>${c.provider_name}</strong> - ${c.contract_type}</li>`
        }
        if (later.length > 5) html += `<li>...and ${later.length - 5} more</li>`
        html += `</ul>`
      }

      html += `<p><a href="https://clausemate.vercel.app">View all contracts →</a></p>`

      // Send email via Resend
      const response = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${resendApiKey}`,
        },
        body: JSON.stringify({
          from: 'Clausemate <reminders@clausemate.com>',
          to: userEmail,
          subject: `🔔 Contract Renewal Reminder - ${urgent.length > 0 ? urgent.length + ' urgent' : renewals.length + ' upcoming'}`,
          html,
        }),
      })

      if (response.ok) {
        emailsSent++
      }
    }

    return new Response(
      JSON.stringify({ success: true, emailsSent }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})
