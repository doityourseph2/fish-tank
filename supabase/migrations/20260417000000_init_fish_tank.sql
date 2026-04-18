-- Fish Tank installation: submissions + public texture bucket
-- Apply in Supabase SQL Editor or: supabase db push (when linked)

create extension if not exists "pgcrypto";

create table if not exists public.fish_submissions (
  id uuid primary key default gen_random_uuid(),
  display_name text not null check (char_length(trim(display_name)) between 1 and 48),
  storage_path text not null,
  status text not null default 'pending'
    check (status in ('pending', 'consumed', 'failed')),
  created_at timestamptz not null default now(),
  consumed_at timestamptz
);

create index if not exists fish_submissions_status_created_idx
  on public.fish_submissions (status, created_at);

comment on table public.fish_submissions is
  'User-drawn fish: name + texture in storage; TD polls pending rows via Netlify functions.';

-- Storage: textures served to TouchDesigner via public URLs (or signed URLs from functions)
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'fish-textures',
  'fish-textures',
  true,
  2097152,
  array['image/png', 'image/jpeg', 'image/webp']::text[]
)
on conflict (id) do update set
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

alter table public.fish_submissions enable row level security;

-- No anon/authenticated policies on fish_submissions: only service role (Netlify functions).
-- Optional: add policies if you expose Supabase to the browser later.

-- Public read of textures in this bucket (for TouchDesigner / kiosks using public URLs)
create policy "Public read fish-textures objects"
on storage.objects for select
to public
using (bucket_id = 'fish-textures');
