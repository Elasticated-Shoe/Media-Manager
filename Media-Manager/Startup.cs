using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Media_Manager.Configuration;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace Media_Manager
{
    public class Startup
    {
        public IConfiguration Configuration { get; }
        private AppSettings _AppSettings { get; }
        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;

            _AppSettings = new AppSettings();
            Configuration.Bind(_AppSettings);
        }

        // This method gets called by the runtime. Use this method to add services to the container.
        public void ConfigureServices(IServiceCollection services)
        {
            services.AddControllers().AddJsonOptions(opts => opts.JsonSerializerOptions.PropertyNamingPolicy = null);

            services.ConfigureDatabase(_AppSettings);

            services.ConfigureCors(_AppSettings);

            services.ConfigureCompression(_AppSettings);
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }

            app.UseKestrel(_AppSettings);

            app.UseCors(_AppSettings);

            app.UseCompression(_AppSettings);

            app.UseRouting();

            app.UseAuthorization();

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllers();
            });
        }
    }
}
