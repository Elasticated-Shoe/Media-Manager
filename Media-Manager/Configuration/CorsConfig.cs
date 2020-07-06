using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Media_Manager.Configuration
{
    public static class CorsConfig
    {
        public static IServiceCollection ConfigureCors(this IServiceCollection services, AppSettings _AppSettings)
        {
            services.AddCors(options =>
            {
                if(_AppSettings.Cors.Policy == "Development")
                    options.AddPolicy("Development", builder => builder.AllowAnyOrigin()
                                                                        .AllowAnyMethod()
                                                                        .AllowAnyHeader()
                    );
                if (_AppSettings.Cors.Policy == "Production")
                    options.AddPolicy("Production", builder => builder.AllowAnyMethod()
                                                                        .AllowAnyHeader()
                                                                        .WithOrigins(_AppSettings.Cors.Allowed)
                    );
            });

            return services;
        }

        public static void UseCors(this IApplicationBuilder app, AppSettings _AppSettings)
        {
            app.UseCors(_AppSettings.Cors.Policy);
        }
    }
}
