FROM nginx:alpine

# تهيئة مخصصة: صفحات المجلدات، وتحويل الدخول إلى الرائد، وكاش الأصول
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY security.conf /etc/nginx/snippets/security.conf
COPY . /usr/share/nginx/html
RUN rm -f /usr/share/nginx/html/nginx.conf /usr/share/nginx/html/security.conf

EXPOSE 80
