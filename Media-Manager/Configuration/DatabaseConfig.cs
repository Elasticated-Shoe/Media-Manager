using Media_Manager.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Media_Manager.Configuration
{
    public static class DatabaseConfig
    {
        public static IServiceCollection ConfigureDatabase(this IServiceCollection services, AppSettings _AppSettings)
        {
            services.AddDbContext<MediaDbContext>(options =>
                options.UseSqlServer(_AppSettings.ConnectionString)
            );

            return services;
        }
    }
    public class MediaDbContext : DbContext
    {
        public DbSet<PeopleMetadata> PeopleMetadata { get; set; }

        public MediaDbContext(DbContextOptions<MediaDbContext> options)
            : base(options)
        {

        }
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<PeopleMetadata>(entity =>
            {
                entity.HasIndex(x => x.PersonId);
            });
        }
    }
}
